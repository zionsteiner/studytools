from itertools import count
from typing import Any, List, Callable

import numpy as np


class Option:
    def __init__(self, name: str, prompt: str, validator: Callable[[Any], bool] = None,
                 processor: Callable = str):
        self.name = name
        self.prompt = prompt
        self.processor = processor
        if validator:
            self.validator = validator
        else:
            self.validator = lambda x: True

        self.__selection = None

    def set_prompt(self, prompt):
        self.prompt = prompt

    @property
    def selection(self):
        return self.__selection

    @selection.setter
    def selection(self, value):
        if self.validator(value):
            self.__selection = self.processor(value)
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
                print('Invalid option, try again\n')


class MultipleChoice(Option):
    def __init__(self, question: str, options: List[str], answer_index=0):
        super().__init__(name=question,
                         prompt=self.prompt_str(question, options),
                         validator=lambda option, n_options=len(options): option.isdigit() and (1 <= int(option) <= n_options),
                         processor=lambda option: int(option))

        self.question = None
        self.set_question(question)
        self.options = None
        self.answer_index = None
        self.set_options(options, answer_index)

    def prompt_str(self, question=None, options=None):
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

    def set_options(self, options: list, answer_index=0):
        self.options = options
        self.answer_index = answer_index

        self.shuffle_options()

    def shuffle_options(self):
        self.__selection = None

        new_indices = list(range(len(self.options)))
        np.random.shuffle(new_indices)
        self.options = [self.options[x] for x in new_indices]
        self.answer_index = new_indices.index(self.answer_index)

        self.set_prompt(self.prompt_str())

    def is_correct(self):
        if self.selection == (self.answer_index + 1):
            return True
        else:
            return False
