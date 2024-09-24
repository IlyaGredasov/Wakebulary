from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class WordStatistics:
    word: str
    correct: int
    attempts: int

    @property
    def score(self) -> float:
        return self.correct / max(1, self.attempts)

    def __hash__(self):
        return hash((self.word, self.correct, self.attempts))


class WordTranslation:

    def __init__(self, word: str, translation: list[str]):
        self.word = word
        self.translation = translation

    def __str__(self):
        return f"{self.word} - {tuple(self.translation)}"


@dataclass
class SessionStatistics:
    correct_count: int
    attempts_count: int

    @property
    def precision(self) -> float:
        return self.correct_count / max(1, self.attempts_count)

    session_time_start: float
