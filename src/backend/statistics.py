from dataclasses import dataclass
from time import time
from datetime import timedelta


class WordTranslation:

    def __init__(self, word: str = None, translation: list[str] = None):
        self.word = word
        self.translation = translation

    def __repr__(self):
        return f"{self.word} - {tuple(self.translation)}"


@dataclass
class SessionStatistics:
    correct_count: int
    attempts_count: int
    session_time: float

    @property
    def precision(self) -> float:
        return self.correct_count / max(1, self.attempts_count)

    def timer(self) -> None:
        self.session_time: timedelta = timedelta(seconds=time() - self.session_time)

    def __repr__(self):
        return (f"Time: {self.session_time} - {self.correct_count} correct - "
                f"{self.attempts_count} attempts - {round(self.precision * 100, 2)}% precision")
