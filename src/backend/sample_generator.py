from __future__ import annotations

import os
from time import time, sleep
from typing import Literal
from random import expovariate, choice

from logger import logger
from src.backend.statistics import WordStatistics, SessionStatistics, WordTranslation
from src.backend.db_client import DataBaseClient


class SampleGenerator:
    def __init__(self, mode: Literal["rus", "eng"], alpha: float = 8, clear_delay: float = 1) -> None:
        self.global_list = []
        self.raw_dict: dict[WordStatistics, list[str]] = DataBaseClient.load_to_dict(mode)
        self.alpha = alpha
        self.session_stats = SessionStatistics(0, 0, time())
        self.clear_delay = clear_delay

    def start_learning_loop(self, sample_size: int = 30) -> None:
        self.global_list: list[WordStatistics] = list(self.raw_dict.keys())
        self.global_list.sort(key=lambda x: x.score)
        self.global_list: list[WordTranslation] = [WordTranslation(word_stat.word, self.raw_dict[word_stat]) for
                                                   word_stat in
                                                   self.global_list]
        sample: list[WordTranslation] = []
        while self.global_list:
            while len(self.global_list) > 0 and len(sample) < sample_size:
                index = round(expovariate(self.alpha / len(self.global_list)))
                while 0 > index >= len(self.global_list):
                    index = round(expovariate(self.alpha / len(self.global_list)))
                    logger.debug(f"{index} out of {len(self.global_list)}")
                sample.append(self.global_list.pop(index))
            while sample:
                question_word = choice(sample)
                print(f"{question_word.word} ?")
                print(f"Remain: {len(self.global_list)}, remain in sample: {len(sample)}, Your answer:")
                answer = input().capitalize()
                if answer == "!end":
                    raise KeyboardInterrupt
                correct, attempts = DataBaseClient.get_statistics(question_word.word)
                if answer in question_word.translation:
                    print(f"Yes! {answer}")
                    question_word.translation.remove(answer)
                    if len(question_word.translation) == 0:
                        sample.remove(question_word)
                    self.session_stats.correct_count += 1
                    self.session_stats.attempts_count += 1
                    DataBaseClient.set_statistics(question_word.word, correct + 1, attempts + 1)
                else:
                    print(f"No: {question_word.translation}")
                    self.session_stats.attempts_count += 1
                    DataBaseClient.set_statistics(question_word.word, correct, attempts + 1)
                if self.clear_delay > 0:
                    sleep(self.clear_delay)
                    os.system('cls' if os.name == 'nt' else 'clear')
