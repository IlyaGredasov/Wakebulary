import os
from pathlib import Path
from config import SRC_DIR
import pytest
import tempfile

from src.backend.db_client import DataBaseClient, low_and_cap_args


@pytest.fixture
def db_fixture():
    db_instance = DataBaseClient("tests/test_database.db")
    db_instance.cursor.execute(
        f"""
        INSERT INTO eng (id, word)
        VALUES (1,'Easy'), (2,'Light'), (3,'Empty');
        """
    )
    db_instance.cursor.execute(
        f"""
        INSERT INTO rus (id, word)
        VALUES (1,'Легкий'), (2, 'Простой');
        """
    )
    db_instance.cursor.execute(
        f"""
        INSERT INTO eng_rus (id,eng_id, rus_id)
        VALUES (1, 1, 1), (2, 1, 2), (3, 2, 1);
        """
    )
    db_instance.connection.commit()
    yield db_instance
    db_instance.cursor.execute("DELETE FROM eng")
    db_instance.cursor.execute("DELETE FROM rus")
    db_instance.cursor.execute("DELETE FROM eng_rus")
    db_instance.connection.commit()


def test_low_and_cap_args_wrapper():
    @low_and_cap_args
    def func(s: str, ls: list[str]):
        return s, ls

    assert func("aBC", ["cDE", "fGh"]) == ("Abc", ["Cde", "Fgh"])


def test_init_non_empty_db(db_fixture):
    tables = db_fixture.cursor.execute("SELECT name FROM sqlite_master")
    assert tables.fetchall()


def test_word_type(db_fixture):
    assert db_fixture.word_type("Это - очень надежный тест, я надеюсь...") == "rus"
    assert db_fixture.word_type("This is quite reliable test, I hope") == "eng"
    assert db_fixture.word_type("abcабв") is None


def test_check_transl(db_fixture):
    assert not db_fixture.check_transl("abc", ["абв", "ьr"])
    assert not db_fixture.check_transl("abc", ["abc", "абв"])
    assert not db_fixture.check_transl("abc", ["abc"])
    assert db_fixture.check_transl("abc", ["абв"])


def test_insert_transl(db_fixture):
    db_fixture.insert_transl("empty", ["пустой"])
    assert db_fixture.find_word("empty")
    assert db_fixture.find_word("пустой")
    assert "Пустой" in db_fixture.translate_word("empty")


def test_erase_transl(db_fixture):
    db_fixture.erase_transl("Light", ["Легкий"])
    query = db_fixture.cursor.execute(
        """
        SELECT eng_id, rus_id
        FROM eng_rus
        """
    )
    assert query.fetchall() == [(1, 1), (1, 2)]
    query = db_fixture.cursor.execute(
        """
        SELECT id, word
        FROM eng
        """
    )
    assert query.fetchall() == [(1, "Easy")]


def test_clear_orphans(db_fixture):
    db_fixture.clear_orphans()
    query = db_fixture.cursor.execute(
        """
        SELECT id, word
        FROM eng
        """
    )
    assert query.fetchall() == [(1, "Easy"), (2, "Light")]


def test_get_statistics(db_fixture):
    db_fixture.cursor.execute(
        f"""
        UPDATE eng
        SET correct = 1, attempts = 1
        WHERE word = 'Light'
        """
    )
    assert db_fixture.get_statistics("Light") == (1, 1)


def test_set_statistics(db_fixture):
    db_fixture.set_statistics("Light", 1, 1)
    assert db_fixture.get_statistics("Light") == (1, 1)


def test_translate_word(db_fixture):
    assert db_fixture.translate_word("easy") == ["Легкий", "Простой"]
    assert db_fixture.translate_word("легкий") == ["Easy", "Light"]


def test_find_word(db_fixture):
    assert db_fixture.find_word("easy")
    assert db_fixture.find_word("легкий")
