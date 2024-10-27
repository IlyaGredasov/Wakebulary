from __future__ import annotations

import asyncio
import os
from time import time, sleep
from typing import Literal
from random import expovariate, choice

import asynckivy as ak
from application.LearnScreen import LearnScreen
from logger import logger
from src.backend.statistics import WordStatistics, SessionStatistics, WordTranslation
from src.backend.db_client import DataBaseClient


class SampleGenerator:
    def __init__(self, mode: Literal["rus", "eng"], alpha: float = 8, clear_delay: float = 1) -> None:
        """

        :rtype: object
        """
        self.question_word = None
        self.__global_list = []
        self.__db = DataBaseClient()
        self.__raw_dict: dict[WordStatistics, list[str]] = self.__db.load_to_dict(mode)
        self.alpha = alpha
        self.session_stats = SessionStatistics(0, 0, time())
        self.clear_delay = clear_delay

    async def start_learning_loop(self, sample_size: int = 30, screen: LearnScreen = None) -> None:
        self.__global_list: list[WordStatistics] = list(self.__raw_dict.keys())
        self.__global_list.sort(key=lambda x: x.score)
        self.__global_list: list[WordTranslation] = [WordTranslation(word_stat.word, self.__raw_dict[word_stat]) for
                                                     word_stat in
                                                     self.__global_list]
        sample: list[WordTranslation] = []
        while self.__global_list:
            while len(self.__global_list) > 0 and len(sample) < sample_size:
                index = round(expovariate(self.alpha / len(self.__global_list)))
                while 0 > index >= len(self.__global_list):
                    index = round(expovariate(self.alpha / len(self.__global_list)))
                    logger.debug(f"{index} out of {len(self.__global_list)}")
                sample.append(self.__global_list.pop(index))
            while sample and screen.loop_event.is_set():
                self.question_word = choice(sample)
                print(f"{self.question_word.word} ?")
                print(f"Remain: {len(self.__global_list)}, remain in sample: {len(sample)}, Your answer:")

                await asyncio.sleep(1)
                #answer = input().capitalize()
                await screen.press_event.wait()
                # answer = LearnScreen.confirm_answer(screen.ids.translation_input)
                answer = screen.ids.translation_input.text

                if answer == "!end":
                    raise KeyboardInterrupt
                correct, attempts = self.__db.get_statistics(self.question_word.word)
                if answer in self.question_word.translation:
                    print(f"Yes! {answer}")
                    self.question_word.translation.remove(answer)
                    if len(self.question_word.translation) == 0:
                        sample.remove(self.question_word)
                    self.session_stats.correct_count += 1
                    self.session_stats.attempts_count += 1
                    self.__db.set_statistics(self.question_word.word, correct + 1, attempts + 1)
                else:
                    print(f"No: {self.question_word.translation}")
                    self.session_stats.attempts_count += 1
                    self.__db.set_statistics(self.question_word.word, correct, attempts + 1)
                if self.clear_delay > 0:
                    sleep(self.clear_delay)
                    os.system('cls' if os.name == 'nt' else 'clear')
                screen.press_event.clear()
        self.session_stats.timer()
        print(self.session_stats)
