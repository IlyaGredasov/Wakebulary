from datetime import time
from dataclasses import dataclass


@dataclass
class WordStatistics:
    word: str
    correct: int
    attempts: int

    @property
    def score(self) -> float:
        return self.correct / max(1, self.attempts)


@dataclass
class SessionStatistics:
    answer_count: int
    mistake_count: int

    @property
    def mistake_per_word(self) -> float:
        return self.mistake_count / max(1, self.answer_count)

    session_time: time
