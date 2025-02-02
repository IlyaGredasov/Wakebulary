from __future__ import annotations

import os

from time import time, sleep
from typing import Literal, List
from random import expovariate, choice, random, randint
from logger import logger
from sys import argv
from src.backend.statistics import SessionStatistics, WordTranslation
from src.backend.db_client import DataBaseClient

RANDOMNESS_CONST = float(argv[2])


class SampleGenerator:
    def __init__(self, mode: Literal["rus", "eng"], alpha: float = 8, clear_delay: float = 1):
        self.__db = DataBaseClient("database.db")
        self.__global_list = self.__db.load_list(mode)
        self.alpha = alpha
        self.session_stats = SessionStatistics(0, 0, time())
        self.clear_delay = clear_delay

    def start_learning_loop(self, sample_size: int = 50) -> None:
        sample: List[WordTranslation] = []
        os.system('cls' if os.name == 'nt' else 'clear')
        while self.__global_list:
            while self.__global_list and len(sample) < sample_size:
                if random() < RANDOMNESS_CONST:
                    index = round(expovariate(self.alpha / len(self.__global_list)))
                    while 0 > index and index >= len(self.__global_list):
                        index = round(expovariate(self.alpha / len(self.__global_list)))
                        logger.debug(f"{index} out of {len(self.__global_list)}")
                else:
                    index = randint(0, len(self.__global_list) - 1)
                word: str = self.__global_list.pop(index)
                sample.append(WordTranslation(word, self.__db.translate_word(word)))
            while sample:
                question_word = choice(sample)
                print(f"{question_word.word}?")
                print(f"Remain: {len(self.__global_list)}, Remain in sample: {len(sample)}, "
                      f"Correct: {100 * self.session_stats.precision:.1f}%, Your answer:")
                answer = input().capitalize()
                if answer == "!end":
                    raise KeyboardInterrupt
                correct, attempts = self.__db.get_statistics(question_word.word)
                if answer in question_word.translation:
                    print(f"Yes! {answer}")
                    question_word.translation.remove(answer)
                    if len(question_word.translation) == 0:
                        sample.remove(question_word)
                    self.session_stats.correct_count += 1
                    self.session_stats.attempts_count += 1
                    self.__db.set_statistics(question_word.word, correct + 1, attempts + 1)
                else:
                    print(f"No: {question_word.translation}")
                    self.session_stats.attempts_count += 1
                    self.__db.set_statistics(question_word.word, correct, attempts + 1)
                if self.clear_delay > 0:
                    sleep(self.clear_delay)
                    os.system('cls' if os.name == 'nt' else 'clear')
        self.session_stats.timer()
        print(self.session_stats)
