from __future__ import annotations

import sqlite3
import os
from enum import EnumType
from typing import Literal, Callable
from config import SRC_DIR


def low_and_cap_args(func: Callable[[str, list[str]], ...]):
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

    def __init__(self, database_name: str):
        self.connection: sqlite3.Connection = sqlite3.connect(os.path.join(SRC_DIR, database_name))
        self.cursor = self.connection.cursor()
        tables = self.cursor.execute("SELECT name FROM sqlite_master").fetchall()
        if not tables:
            self.init_db()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.clear_orphans()

    @low_and_cap_args
    def insert_mapping(self, word: str, mappings: list[str],
                       word_type: Literal["request"] | Literal["response"] = "request") -> None:
        mappings_type = "response" if word_type == "request" else "request"
        if not self.find_word(word):
            self.cursor.execute(
                f"INSERT INTO {word_type} (word) VALUES (\"{word}\");",
            )
        for mapping in mappings:
            if not self.find_word(mapping, mappings_type):
                self.cursor.execute(
                    f"INSERT INTO {mappings_type} (word) VALUES (\"{mapping}\")",
                )
            res = self.cursor.execute(
                f"""
                SELECT request_response.request_id, request_response.response_id
                FROM
                    request
                    INNER JOIN request_response ON request.id = request_response.request_id
                    INNER JOIN response ON request_response.response_id = response.id
                WHERE request.word = ? AND response.word = ?
                """,
                (word, mapping) if word_type == "request" else (mapping, word)
            )
            query = res.fetchall()
            if len(query) == 0:
                self.cursor.execute(
                    f"""
                    INSERT INTO request_response (request_id, response_id)
                    SELECT request.id, response.id
                    FROM request CROSS JOIN response
                    WHERE request.word = ? AND response.word = ?
                    """,
                    (word, mapping) if word_type == "request" else (mapping, word)
                )
        self.connection.commit()

    @low_and_cap_args
    def erase_mapping(self, word: str, mappings: list[str],
                      word_type: Literal["request"] | Literal["response"] = "request") -> None:
        for mapping in mappings:
            self.cursor.execute(
                f"""
                    DELETE FROM request_response 
                    WHERE (request_id, response_id) IN (
                        SELECT request.id, response.id
                        FROM request CROSS JOIN response
                        WHERE request.word = ? AND response.word = ?
                    )
                    """,
                (word, mapping) if word_type == "request" else (mapping, word)
            )
            self.clear_orphans()
        self.connection.commit()

    @low_and_cap_args
    def delete_word(self, word: str, word_type: Literal["request"] | Literal["response"] = "request") -> None:
        self.erase_mapping(word, self.map_word(word, word_type=word_type), word_type=word_type)

    @low_and_cap_args
    def clear_orphans(self) -> None:
        self.cursor.execute(
            """
            DELETE FROM response
            WHERE response.word IN (
                SELECT response.word
                FROM response
                        LEFT JOIN request_response ON response.id = request_response.response_id
                WHERE response_id IS NULL
            )
            """
        )
        self.cursor.execute(
            """
            DELETE FROM request
            WHERE request.word IN (
                SELECT request.word
                FROM request
                        LEFT JOIN request_response ON request.id = request_response.request_id
                WHERE request_id IS NULL
            )
            """
        )
        self.connection.commit()

    @low_and_cap_args
    def get_statistics(self, word: str,
                       word_type: Literal["request"] | Literal["response"] = "request") -> tuple[int, int]:
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
    def set_statistics(self, word: str, correct: int, attempts: int,
                       word_type: Literal["request"] | Literal["response"] = "request") -> None:
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
    def map_word(self, word: str, word_type: Literal["request"] | Literal["response"] = "request") -> list[str]:
        mapping_type = "response" if word_type == "request" else "request"
        self.cursor.execute(
            f"""
            SELECT {mapping_type}.word
            FROM
                {word_type}
                INNER JOIN request_response ON {word_type}.id = request_response.{word_type}_id
                INNER JOIN {mapping_type} ON request_response.{mapping_type}_id = {mapping_type}.id
            WHERE {word_type}.word = \"{word}\"
            """
        )
        return [el[0] for el in self.cursor.fetchall()]

    @low_and_cap_args
    def find_word(self, word: str, word_type: Literal["request"] | Literal["response"] = "request") -> bool:
        res = self.cursor.execute(
            f"""
            SELECT {word_type}.word
            FROM {word_type}
            WHERE word = \"{word}\"
            """
        )
        return len(res.fetchall()) > 0

    def load_list(self, mode: Literal["forward", "backward"]) -> list[str]:
        word_type = "request" if mode == "forward" else "response"
        res = self.cursor.execute(
            f"""
            SELECT word
            FROM {word_type}
            ORDER BY CAST({word_type}.correct AS double)/CAST(MAX(1,{word_type}.attempts) AS double);
            """
        )
        return [el[0] for el in res.fetchall()]

    def init_db(self) -> None:
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS response
            """
        )
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS request
            """
        )
        self.cursor.execute(
            """
            DROP TABLE IF EXISTS request_response
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE response(
                id INTEGER PRIMARY KEY,
                word VARCHAR(255) UNIQUE NOT NULL,
                correct INTEGER DEFAULT 0,
                attempts INTEGER DEFAULT 0
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE request(
                id INTEGER PRIMARY KEY,
                word VARCHAR(255) UNIQUE NOT NULL,
                correct INTEGER DEFAULT 0,
                attempts INTEGER DEFAULT 0
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE request_response(
                id INTEGER PRIMARY KEY,
                request_id INTEGER NOT NULL,
                response_id INTEGER NOT NULL,
                FOREIGN KEY(request_id) REFERENCES request(id) ON DELETE CASCADE,
                FOREIGN KEY(response_id) REFERENCES response(id) ON DELETE CASCADE,
                UNIQUE (request_id, response_id)
            )
            """
        )
        self.connection.commit()
