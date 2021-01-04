from itertools import count
import os
from typing import Any, List, Callable

import numpy as np


class Option:
    def __init__(self,
                 name: str,
                 prompt: str,
                 validator: Callable[[Any], bool] = None,
                 processor: Callable = str,
                 msg=None):
        self.name = name
        self.prompt = prompt
        self.processor = processor
        self.msg = msg if msg else 'Invalid option, try again'
        if validator:
            self.validator = validator
        else:
            self.validator = lambda x: True

        self._selection = None

    def set_prompt(self, prompt):
        self.prompt = prompt

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, value):
        if self.validator(value):
            self._selection = self.processor(value)
        else:
            raise ValueError()

    def prompt_user(self):
        validated = False
        while not validated:
            try:
                self.selection = input(self.prompt + '\n')
                print()
                validated = True
            except ValueError:
                print(self.msg + '\n')


class MultipleChoice(Option):
    def __init__(self, question: str, options: List[str], answer_index=0):
        super().__init__(name=question,
                         prompt=self._prompt_str(question, options),
                         validator=lambda option, n_options=len(options): option.isdigit() and (1 <= int(option) <= n_options),
                         processor=lambda option: int(option))

        self.question = question
        self.options = None
        self.set_options(options)
        self.answer_index = None
        self.set_options(options, answer_index)

    def _prompt_str(self, question=None, options=None):
        if not question:
            question = self.question
        if not options:
            options = self.options

        curr_index = count(1)
        options_str = 'Select an answer:\n' + '\n'.join([f'{next(curr_index)}:\t{option}' for option in options])

        prompt_str = question + '\n' + options_str
        return prompt_str

    def set_question(self, question: str):
        self.question = question

        self.set_prompt(self._prompt_str())

    def set_options(self, options: list, answer_index=0):
        self.options = options
        self.answer_index = answer_index

        self.shuffle_options()

        self.set_prompt(self._prompt_str())

    def shuffle_options(self):
        self._selection = None

        new_indices = list(range(len(self.options)))
        np.random.shuffle(new_indices)
        self.options = [self.options[x] for x in new_indices]
        self.answer_index = new_indices.index(self.answer_index)

        self.set_prompt(self._prompt_str())

    def is_correct(self):
        if self.selection == (self.answer_index + 1):
            return True
        else:
            return False
