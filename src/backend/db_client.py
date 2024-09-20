from __future__ import annotations

import sqlite3
import string
from typing import Literal


class DataBaseClient:
    connection: sqlite3.Connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    @staticmethod
    def is_eng(word: str) -> bool:
        return all(c in string.ascii_letters for c in word)

    @staticmethod
    def insert_word(word: str, translation: list[str]) -> None:
        if DataBaseClient.is_eng(word) and all(not DataBaseClient.is_eng(c) for c in translation):
            if not DataBaseClient.find_word(word):
                DataBaseClient.cursor.execute(
                    "INSERT INTO eng (word, correct, attempts) VALUES (?, 0, 0);",
                    (word,)
                )
            for transl in translation:
                if not DataBaseClient.find_word(transl):
                    DataBaseClient.cursor.execute(
                        """
                            INSERT INTO rus (word, correct, attempts) VALUES (?, 0, 0)
                            """,
                        (transl,)
                    )
            for transl in translation:
                DataBaseClient.cursor.execute(
                    """
                    INSERT INTO eng_rus (eng_id, rus_id)
                    SELECT eng.id, rus.id
                    FROM eng CROSS JOIN rus
                    WHERE eng.word = ? AND rus.word = ?
                    """,
                    (word, transl)
                )
        elif not DataBaseClient.is_eng(word) and all(DataBaseClient.is_eng(c) for c in translation):
            if not DataBaseClient.find_word(word):
                DataBaseClient.cursor.execute(
                    "INSERT INTO rus (word, correct, attempts) VALUES (?, 0, 0);",
                    (word,)
                )
            for transl in translation:
                if not DataBaseClient.find_word(transl):
                    DataBaseClient.cursor.execute(
                        "INSERT INTO eng (word, correct, attempts) VALUES (?, 0, 0);",
                        (transl,)
                    )
            for transl in translation:
                DataBaseClient.cursor.execute(
                    """
                    INSERT INTO eng_rus (eng_id, rus_id)
                    SELECT eng.id, rus.id
                    FROM eng CROSS JOIN rus
                    WHERE rus.word = ? AND eng.word = ?
                    """,
                    (word, transl)
                )
        else:
            raise ValueError("Query is not valid")
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
    def delete_word(word: str) -> None:
        if DataBaseClient.is_eng(word):
            DataBaseClient.cursor.execute(
                "DELETE FROM eng WHERE eng.word = ?",
                (word,)
            )
            DataBaseClient.connection.commit()
        else:
            DataBaseClient.cursor.execute(
                "DELETE FROM rus WHERE rus.word = ?",
                (word,)
            )
            DataBaseClient.connection.commit()

    @staticmethod
    def clear_statistics() -> None:
        DataBaseClient.cursor.execute(
            """
            UPDATE eng
            SET
                correct = 0, attempts = 0;
            """
        )
        DataBaseClient.cursor.execute(
            """
            UPDATE rus
            SET
                correct = 0, attempts = 0;
            """
        )
        DataBaseClient.connection.commit()

    @staticmethod
    def set_statistics(word: str, correct: int, attempts: int) -> None:
        if DataBaseClient.is_eng(word):
            DataBaseClient.cursor.execute(
                """
                UPDATE eng
                SET
                    correct = ?, attempts = ?
                WHERE eng.word = ?
                """,
                (correct, attempts, word,)
            )
        else:
            DataBaseClient.cursor.execute(
                """
                UPDATE rus
                SET
                    correct = ?, attempts = ?
                WHERE rus.word = ?
                """,
                (correct, attempts, word,)
            )
        DataBaseClient.connection.commit()

    @staticmethod
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
    def load_to_dict(mode: Literal["rus"] | Literal["eng"]) -> dict[str, list[str]]:
        if mode == "rus":
            DataBaseClient.cursor.execute(
                "SELECT rus.word FROM rus"
            )
        else:
            DataBaseClient.cursor.execute(
                "SELECT eng.word FROM eng"
            )
        words = [el[0] for el in DataBaseClient.cursor.fetchall()]
        return {word: DataBaseClient.translate_word(word) for word in words}
