from __future__ import annotations
from logger import logger
from src.backend.statistics import WordStatistics
import sqlite3
import string
from typing import Literal


def low_and_cap_args(func):
    def wrapper(*args, **kwargs):
        new_args = [
            arg.lower().capitalize().replace(u'\xa0', u' ') if isinstance(arg, str) else
            (list(map(lambda x: x.lower().capitalize().replace(u'\xa0', u' ') if isinstance(x, str) else x,
                      arg)) if isinstance(arg, list) else
             tuple(map(lambda x: x.lower().capitalize().replace(u'\xa0', u' ') if isinstance(x, str) else x,
                       arg)) if isinstance(arg, tuple) else
             arg)
            for arg in args
        ]
        new_kwargs = {
            k: v.lower().capitalize().replace(u'\xa0', u' ') if isinstance(v, str) else
            (list(map(lambda x: x.lower().capitalize().replace(u'\xa0', u' ') if isinstance(x, str) else x,
                      v)) if isinstance(v, list) else
             tuple(map(lambda x: x.lower().capitalize().replace(u'\xa0', u' ') if isinstance(x, str) else x,
                       v)) if isinstance(v, tuple) else
             v)
            for k, v in kwargs.items()
        }
        return func(*new_args, **new_kwargs)

    return wrapper

class DataBaseClient:
    connection: sqlite3.Connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    @staticmethod
    @low_and_cap_args
    def word_type(word: str) -> Literal["rus", "eng"] | None:
        if all(c in string.ascii_letters + string.punctuation + ' ' for c in word):
            return "eng"
        if all(c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ " + string.punctuation for c in
               word):
            return "rus"
        return None

    @staticmethod
    @low_and_cap_args
    def insert_word(word: str, translation: list[str]) -> None:
        word_type = DataBaseClient.word_type(word)
        translations_type = list(map(DataBaseClient.word_type, translation))
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
        if not DataBaseClient.find_word(word):
            DataBaseClient.cursor.execute(
                f"INSERT INTO {word_type} (word) VALUES (\"{word}\");",
            )
        for i, transl in enumerate(translation):
            if not DataBaseClient.find_word(transl):
                DataBaseClient.cursor.execute(
                    f"INSERT INTO {translations_type} (word) VALUES (\"{transl}\")",
                )
        for i, transl in enumerate(translation):
            res = DataBaseClient.cursor.execute(
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
                DataBaseClient.cursor.execute(
                    f"""
                    INSERT INTO eng_rus (eng_id, rus_id)
                    SELECT eng.id, rus.id
                    FROM eng CROSS JOIN rus
                    WHERE eng.word = ? AND rus.word = ?
                    """,
                    (word, transl) if word_type == "eng" else (transl, word)
                )
                logger.info(f"Translations were inserted successfully, {word}, {transl}")
        DataBaseClient.connection.commit()

    @staticmethod
    @low_and_cap_args
    def erase_word(word: str, translation: list[str]) -> None:
        word_type = DataBaseClient.word_type(word)
        translations_type = list(map(DataBaseClient.word_type, translation))
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
            DataBaseClient.cursor.execute(
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
        DataBaseClient.connection.commit()

    @staticmethod
    @low_and_cap_args
    def delete_word(word: str) -> None:
        word_type = DataBaseClient.word_type(word)
        if word_type is not None:
            DataBaseClient.cursor.execute(
                f"""
                DELETE FROM eng_rus
                WHERE eng_rus.id IN (
                    SELECT eng_rus.id
                    FROM
                    eng_rus
                        INNER JOIN {word_type} ON {word_type}.id = eng_rus.{word_type}_id
                    WHERE {word_type}.word = \"{word}\"
                )
                """
            )
            DataBaseClient.cursor.execute(
                f"DELETE FROM {word_type} WHERE {word_type}.word = \"{word}\""
            )
            DataBaseClient.connection.commit()

    @staticmethod
    @low_and_cap_args
    def get_statistics(word: str) -> tuple[int, int]:
        word_type = DataBaseClient.word_type(word)
        if word_type is not None:
            res = DataBaseClient.cursor.execute(
                f"""
                SELECT correct, attempts
                FROM {word_type}
                WHERE {word_type}.word = \"{word}\"
                """
            )
            query = res.fetchall()
            return query[0] if len(query) > 0 else (0, 0)

    @staticmethod
    @low_and_cap_args
    def set_statistics(word: str, correct: int, attempts: int) -> None:
        word_type = DataBaseClient.word_type(word)
        if word_type is not None:
            DataBaseClient.cursor.execute(
                f"""
                UPDATE {word_type}
                SET
                    correct = {correct}, attempts = {attempts}
                WHERE {word_type}.word = \"{word}\"
                """
            )
            DataBaseClient.connection.commit()

    @staticmethod
    @low_and_cap_args
    def translate_word(word: str) -> list[str]:
        word_type = DataBaseClient.word_type(word)
        opposite_word_type = "rus" if word_type == "eng" else "eng"
        DataBaseClient.cursor.execute(
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
        return [el[0] for el in DataBaseClient.cursor.fetchall()]

    @staticmethod
    @low_and_cap_args
    def find_word(word: str) -> bool:
        word_type = DataBaseClient.word_type(word)
        res = DataBaseClient.cursor.execute(
            f"""
            SELECT {word_type}.word
            FROM {word_type}
            WHERE word = ?
            """,
            (word,)
        )
        query = res.fetchall()
        return len(query) > 0

    @staticmethod
    def load_to_dict(mode: Literal["rus", "eng"]) -> dict[WordStatistics, list[str]]:
        res = DataBaseClient.cursor.execute(
            f"SELECT * FROM {mode}"
        )
        words = [WordStatistics(*el[1:]) for el in res.fetchall()]
        return {word_stat: DataBaseClient.translate_word(word_stat.word) for word_stat in words}
    @staticmethod
    def clear_statistics() -> None:
        DataBaseClient.cursor.execute(
            """
            UPDATE rus SET correct = 0, attempts = 0
            """
        )
        logger.info("All statistics in rus table were cleared")
        DataBaseClient.cursor.execute(
            """
            UPDATE eng SET correct = 0, attempts = 0
            """
        )
        logger.info("All statistics in eng table were cleared")
        DataBaseClient.connection.commit()

    @staticmethod
    def init_db() -> None:
        DataBaseClient.cursor.execute(
            """
            DROP TABLE IF EXISTS rus
            """
        )
        logger.info("rus table was dropped")
        DataBaseClient.cursor.execute(
            """
            DROP TABLE IF EXISTS eng
            """
        )
        logger.info("eng table was dropped")
        DataBaseClient.cursor.execute(
            """
            DROP TABLE IF EXISTS eng_rus
            """
        )
        logger.info("eng_rus table was dropped")
        DataBaseClient.cursor.execute(
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
        DataBaseClient.cursor.execute(
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
        DataBaseClient.cursor.execute(
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
