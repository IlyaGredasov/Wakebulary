from __future__ import annotations
from logger import logger
from src.backend.statistics import WordStatistics
import sqlite3
import string
from os.path import isfile
from typing import Literal


def low_and_cap_args(func):
    def wrapper(*args):
        new_args = [
            arg.lower().capitalize().replace(u'\xa0', u' ') if isinstance(arg, str) else
            (list(map(lambda x: x.lower().capitalize().replace(u'\xa0', u' ') if isinstance(x, str) else x,
                      arg)) if isinstance(arg, list) else arg)
            for arg in args
        ]
        return func(*new_args)

    return wrapper


class DataBaseClient:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.connection: sqlite3.Connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()
        tables_fetch = self.cursor.execute("SELECT name FROM sqlite_master")
        tables = tables_fetch.fetchall()
        if not tables:
            self.init_db()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.clear_orphans()

    @low_and_cap_args
    def word_type(self, word: str) -> Literal["rus", "eng"] | None:
        if all(c in string.ascii_letters + string.punctuation + ' ' for c in word):
            return "eng"
        if all(c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ " + string.punctuation for c in
               word):
            return "rus"
        return None

    @low_and_cap_args
    def insert_transl(self, word: str, translation: list[str]) -> None:
        word_type = self.word_type(word)
        translations_type = list(map(self.word_type, translation))
        if word_type is None or any(t is None for t in translations_type):
            logger.info(f"Invalid word type in query,{word},{tuple(translation)}")
            return
        if len(set(translations_type)) > 1:
            logger.info(f"Different word type in translation, {word}, {tuple(translation)}")
            return
        if word_type == translations_type[0]:
            logger.info(f"Required word translation, {word}, {tuple(translation)}")
            return
        translations_type = translations_type[0]
        if not self.find_word(word):
            self.cursor.execute(
                f"INSERT INTO {word_type} (word) VALUES (\"{word}\");",
            )
        for i, transl in enumerate(translation):
            if not self.find_word(transl):
                self.cursor.execute(
                    f"INSERT INTO {translations_type} (word) VALUES (\"{transl}\")",
                )
        for i, transl in enumerate(translation):
            res = self.cursor.execute(
                f"""
                SELECT eng_rus.eng_id, eng_rus.rus_id
                FROM
                    eng
                    INNER JOIN eng_rus ON eng.id = eng_rus.eng_id
                    INNER JOIN rus ON eng_rus.rus_id = rus.id
                WHERE eng.word = ? AND rus.word = ?
                """,
                (word, transl) if word_type == "eng" else (transl, word)
            )
            query = res.fetchall()
            if len(query) == 0:
                self.cursor.execute(
                    f"""
                    INSERT INTO eng_rus (eng_id, rus_id)
                    SELECT eng.id, rus.id
                    FROM eng CROSS JOIN rus
                    WHERE eng.word = ? AND rus.word = ?
                    """,
                    (word, transl) if word_type == "eng" else (transl, word)
                )
                logger.info(f"Translations were inserted successfully, {word}, {transl}")
        self.connection.commit()

    @low_and_cap_args
    def erase_transl(self, word: str, translation: list[str]) -> None:
        word_type = self.word_type(word)
        translations_type = list(map(self.word_type, translation))
        if word_type is None or any(t is None for t in translations_type):
            logger.info(f"Invalid word type in query,{word},{tuple(translation)}")
            return
        if len(set(translations_type)) > 1:
            logger.info(f"Different word type in translation, {word}, {tuple(translation)}")
            return
        if word_type == translations_type[0]:
            logger.info(f"Required word translation, {word}, {tuple(translation)}")
            return
        for transl in translation:
            self.cursor.execute(
                f"""
                    DELETE FROM eng_rus 
                    WHERE (eng_id, rus_id) IN (
                        SELECT eng.id, rus.id
                        FROM eng CROSS JOIN rus
                        WHERE eng.word = ? AND rus.word = ?
                    )
                    """,
                (word, transl) if word_type == "eng" else (transl, word)
            )
            logger.info(f"Translations were inserted successfully, {word}, {transl}")
        self.connection.commit()

    @low_and_cap_args
    def clear_orphans(self) -> None:
        self.cursor.execute(
            """
            DELETE FROM rus
            WHERE rus.word IN (
                SELECT rus.word
                FROM rus
                        LEFT JOIN eng_rus ON rus.id = eng_rus.rus_id
                WHERE rus_id IS NULL
            )
            """
        )
        self.cursor.execute(
            """
            DELETE FROM eng
            WHERE eng.word IN (
                SELECT eng.word
                FROM eng
                        LEFT JOIN eng_rus ON eng.id = eng_rus.eng_id
                WHERE eng_id IS NULL
            )
            """
        )
        self.connection.commit()

    @low_and_cap_args
    def get_statistics(self, word: str) -> tuple[int, int]:
        word_type = self.word_type(word)
        if word_type is not None:
            res = self.cursor.execute(
                f"""
                SELECT correct, attempts
                FROM {word_type}
                WHERE {word_type}.word = \"{word}\"
                """
            )
            query = res.fetchall()
            return query[0] if len(query) > 0 else (0, 0)

    @low_and_cap_args
    def set_statistics(self, word: str, correct: int, attempts: int) -> None:
        word_type = self.word_type(word)
        if word_type is not None:
            self.cursor.execute(
                f"""
                UPDATE {word_type}
                SET
                    correct = {correct}, attempts = {attempts}
                WHERE {word_type}.word = \"{word}\"
                """
            )
            self.connection.commit()

    @low_and_cap_args
    def translate_word(self, word: str) -> list[str]:
        word_type = self.word_type(word)
        opposite_word_type = "rus" if word_type == "eng" else "eng"
        self.cursor.execute(
            f"""
            SELECT {opposite_word_type}.word
            FROM
                {word_type}
                INNER JOIN eng_rus ON {word_type}.id = eng_rus.{word_type}_id
                INNER JOIN {opposite_word_type} ON eng_rus.{opposite_word_type}_id = {opposite_word_type}.id
            WHERE {word_type}.word = ?
            """,
            (word,)
        )
        return [el[0] for el in self.cursor.fetchall()]

    @low_and_cap_args
    def find_word(self, word: str) -> bool:
        word_type = self.word_type(word)
        res = self.cursor.execute(
            f"""
            SELECT {word_type}.word
            FROM {word_type}
            WHERE word = ?
            """,
            (word,)
        )
        query = res.fetchall()
        return len(query) > 0

    def load_to_dict(self, mode: Literal["rus", "eng"]) -> dict[WordStatistics, list[str]]:
        res = self.cursor.execute(
            f"SELECT * FROM {mode}"
        )
        words = [WordStatistics(*el[1:]) for el in res.fetchall()]
        return {word_stat: self.translate_word(word_stat.word) for word_stat in words}

    def clear_statistics(self) -> None:
        self.cursor.execute(
            """
            UPDATE rus SET correct = 0, attempts = 0
            """
        )
        logger.info("All statistics in rus table were cleared")
        self.cursor.execute(
            """
            UPDATE eng SET correct = 0, attempts = 0
            """
        )
        logger.info("All statistics in eng table were cleared")
        self.connection.commit()

    def init_db(self) -> None:
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS rus
            """
        )
        logger.info("rus table was dropped")
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS eng
            """
        )
        logger.info("eng table was dropped")
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS eng_rus
            """
        )
        logger.info("eng_rus table was dropped")
        self.cursor.execute(
            """
            CREATE TABLE rus(
                id INTEGER PRIMARY KEY,
                word VARCHAR(255) UNIQUE NOT NULL,
                correct INTEGER DEFAULT 0,
                attempts INTEGER DEFAULT 0
            )
            """
        )
        logger.info("rus table was created")
        self.cursor.execute(
            """
            CREATE TABLE eng(
                id INTEGER PRIMARY KEY,
                word VARCHAR(255) UNIQUE NOT NULL,
                correct INTEGER DEFAULT 0,
                attempts INTEGER DEFAULT 0
            )
            """
        )
        logger.info("eng table was created")
        self.cursor.execute(
            """
            CREATE TABLE eng_rus(
                id INTEGER PRIMARY KEY,
                eng_id INTEGER NOT NULL,
                rus_id INTEGER NOT NULL,
                FOREIGN KEY(eng_id) REFERENCES eng(id) ON DELETE CASCADE,
                FOREIGN KEY(rus_id) REFERENCES rus(id) ON DELETE CASCADE,
                UNIQUE (eng_id, rus_id)
            )
            """
        )
        logger.info("eng_rus table was created")
