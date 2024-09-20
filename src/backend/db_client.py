from __future__ import annotations
from src.backend.logger import logger
import sqlite3
import string
from typing import Literal


def low_and_cap_args(func):
    def wrapper(*args, **kwargs):
        new_args = [arg.lower().capitalize() if isinstance(arg, str) else arg for arg in args]
        new_kwargs = {k: v.lower().capitalize() if isinstance(v, str) else v for k, v in kwargs.items()}
        return func(*new_args, **new_kwargs)

    return wrapper


class DataBaseClient:
    connection: sqlite3.Connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    @staticmethod
    @low_and_cap_args
    def word_type(word: str) -> Literal["rus", "eng"] | None:
        if all(c in string.ascii_letters + string.punctuation for c in word):
            return "eng"
        if all(c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ" + string.punctuation for c in
               word):
            return "rus"
        return None

    @staticmethod
    def is_eng(word: str) -> bool:
        return all(c in string.ascii_letters for c in word)

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
        for transl in translation:
            if not DataBaseClient.find_word(transl):
                DataBaseClient.cursor.execute(
                    f"INSERT INTO {translations_type} (word) VALUES (\"{transl}\")",
                )
        for transl in translation:
            DataBaseClient.cursor.execute(
                f"""
                INSERT INTO eng_rus (eng_id, rus_id)
                SELECT eng.id, rus.id
                FROM eng CROSS JOIN rus
                WHERE (?,?) NOT IN (
                    SELECT eng.word, rus.word
                    FROM eng
                        INNER JOIN eng_rus ON eng.id = eng_rus.eng_id
                        INNER JOIN rus ON eng_rus.rus_id = rus.id
                    WHERE eng.word = ? AND rus.word = ? 
                )
                """,
                (word, transl, word, transl) if word_type == "eng" else (transl, word, transl, word)
            )
            logger.info(f"Translations were inserted successfully, {word}, {transl}")
        DataBaseClient.connection.commit()

    @staticmethod
    def erase_translation(word: str, transl: str) -> None:
        if DataBaseClient.is_eng(word) and not DataBaseClient.is_eng(transl):
            DataBaseClient.cursor.execute(
                """
                DELETE FROM eng_rus
                WHERE (eng_rus.rus_id,eng_rus.eng_id) IN ( 
                    SELECT rus.id, eng.id
                    FROM eng
                        INNER JOIN eng_rus ON eng.id = eng_rus.eng_id
                        INNER JOIN rus ON eng_rus.rus_id = rus.id
                    WHERE eng.word = ? AND rus.word = ?
                )
                """,
                (word, transl,)
            )
        elif not DataBaseClient.is_eng(word) and DataBaseClient.is_eng(transl):
            DataBaseClient.cursor.execute(
                """
                DELETE FROM eng_rus
                WHERE (eng_rus.rus_id,eng_rus.eng_id) IN ( 
                    SELECT rus.id, eng.id
                    FROM eng
                        INNER JOIN eng_rus ON eng.id = eng_rus.eng_id
                        INNER JOIN rus ON eng_rus.rus_id = rus.id
                    WHERE eng.word = ? AND rus.word = ?
                )
                """,
                (transl, word,)
            )
        else:
            raise ValueError("Query is not valid")
        DataBaseClient.connection.commit()

    @staticmethod
    @low_and_cap_args
    def delete_word(word: str) -> None:
        word_type = DataBaseClient.word_type(word)
        if word_type is not None:
            DataBaseClient.cursor.execute(
                f"DELETE FROM {word_type} WHERE {word_type}.word = \"{word}\""
            )
            DataBaseClient.connection.commit()

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
        if DataBaseClient.is_eng(word):
            DataBaseClient.cursor.execute(
                """
                SELECT rus.word
                FROM
                    eng
                    INNER JOIN eng_rus ON eng.id = eng_rus.eng_id
                    INNER JOIN rus ON eng_rus.rus_id = rus.id
                WHERE eng.word = ?
                """,
                (word,)
            )
        else:
            DataBaseClient.cursor.execute(
                """
                SELECT eng.word
                FROM
                    rus
                    INNER JOIN eng_rus ON rus.id = eng_rus.rus_id
                    INNER JOIN eng ON eng_rus.eng_id = eng.id
                WHERE rus.word = ?
                """,
                (word,)
            )
        return [el[0] for el in DataBaseClient.cursor.fetchall()]

    @staticmethod
    def find_word(word: str) -> bool:
        if DataBaseClient.is_eng(word):
            res = DataBaseClient.cursor.execute(
                """
                SELECT eng.word
                FROM eng
                WHERE word = ?
                """,
                (word,)
            )
        else:
            res = DataBaseClient.cursor.execute(
                """
                SELECT rus.word
                FROM rus
                WHERE word = ?
                """,
                (word,)
            )
        translation = res.fetchall()
        return len(translation) > 0

    @staticmethod
    def load_to_dict(mode: Literal["rus", "eng"]) -> dict[str, list[str]]:
        DataBaseClient.cursor.execute(
            f"SELECT {mode}.word FROM {mode}"
        )
        words = [el[0] for el in DataBaseClient.cursor.fetchall()]
        return {word: DataBaseClient.translate_word(word) for word in words}
