import os
from enum import Enum, auto
from typing import List

import numpy as np
from options import Option, MultipleChoice
from words2dict import read_words, build_dict, write_dict, parse_dict, entry_to_str


class ToolID(Enum):
    VOCAB = auto()


class Tool:
    def __init__(self, options):
        self._options = options

    def run(self):
        pass

    def _options_prompt(self):
        args = {}

        for option in self._options:
            option.prompt_user()
            args[option.name] = option.selection

        return args


# ToDo: abstract input and backend so words can be anything that the backend can retrieve
class VocabTool(Tool):
    def __init__(self):
        options = [
            Option(name='src_path',
                   prompt='What file would you like to use?\nEx. words.txt',
                   validator=lambda path: os.path.isfile(path),
                   msg='File does not exist'),
            Option(name='is_dict',
                   prompt='Is this a list of words, or a pregenerated dictionary file?\n1.\tWords\n2.\tDictionary',
                   validator=lambda x: x.isdigit() and (1 <= int(x) <= 2),
                   processor=lambda x: bool(int(x) - 1)),
            Option(name='n_cards',
                   prompt='How many flashcards to go through?',
                   validator=lambda x: x.isdigit() and int(x) > 0,
                   processor=int),
            Option(name='show_def',
                   prompt='Show dictionary entries after answer selection?\n1.\tYes\n2.\tNo',
                   validator=lambda x: x.isdigit() and (1 <= int(x) <= 2),
                   processor=lambda x: True if int(x) == 1 else False)
        ]

        super().__init__(options)

    def run(self):
        args = self._options_prompt()

        flashcards = self.__load_flashcards(path=args['src_path'], is_dict=args['is_dict'], n_words=args['n_cards'])

        play_again = True
        while play_again:
            flashcards = self.__show_flashcards(flashcards, args['show_def'])
            if len(flashcards):
                play_again_option = Option(name='play_again',
                                           prompt='Would you like to play again with the words you missed?\n1.\tYes\n2.\tNo',
                                           validator=lambda x: x.isdigit() and (1 <= int(x) <= 2),
                                           processor=lambda x: True if int(x) == 1 else False)
                play_again_option.prompt_user()

                play_again = play_again_option.selection
            else:
                play_again = False

    def __show_flashcards(self, flashcards: List[MultipleChoice], show_def: bool = False):
        mistakes = []

        print('Flashcards')
        print('----------')
        for i, flashcard in enumerate(flashcards):
            flashcard.shuffle_options()

            print(f'[{i + 1} / {len(flashcards)}]')
            flashcard.prompt_user()
            if flashcard.is_correct():
                print('Correct!\n')
            else:
                mistakes.append(flashcard)
                print(f"Incorrect, the correct answer was '{flashcard.options[flashcard.answer_index]}'\n")

            if show_def:
                print('Dictionary Entry')
                print('-----------------')
                print(entry_to_str(flashcard.entry))
                print()

        accuracy = (len(flashcards) - len(mistakes)) / len(flashcards)
        addendum = 'Good job!' if accuracy > 0.5 else 'You have some work to do!'
        print(f'You got {accuracy * 100:.2f}% right. {addendum}\n')

        return mistakes

    def __load_flashcards(self, path: str, is_dict: bool, n_words: int):
        entries = []
        words = []

        if is_dict:
            entries = [entry for entry in parse_dict(path) if 'Missing definition' not in entry['definition']]
            words = [entry['word'] for entry in entries]

            try:
                entries = list(np.random.choice(entries, size=n_words, replace=False))
            except ValueError:
                raise ValueError(f'Dictionary must contain at least {n_words} entries')
        else:
            try:
                words = read_words(path)
                words_subset = np.random.choice(words, size=n_words, replace=False)
            except ValueError:
                raise ValueError(f'File must contain at least {n_words} words')

            entries = build_dict(words_subset, progress_bar=True)

            save_dict_option = Option(name='save_dict',
                                      prompt='Save generated dictionary? You can load vocab from this quicker next '
                                             'time.\n1.\tYes\n2.\tNo',
                                      validator=lambda x: x.isdigit() and (1 <= int(x) <= 2),
                                      processor=lambda x: True if int(x) == 1 else False)
            save_dict_option.prompt_user()

            if save_dict_option.selection:
                save_path_option = Option(name='save_path',
                                          prompt='Enter a path to save the dictionary to')
                save_path_option.prompt_user()
                save_path = save_path_option.selection

                write_dict(entries, save_path)

        entries = [entry for entry in entries if entry['definition']]

        flashcards = []
        N_OPTIONS = 4
        for entry in entries:
            definition = 'Definition: ' + np.random.choice(entry['definition']).split(' - ')[1]
            options = [entry['word']]

            try:
                filtered_words = [word for word in words if word != entry['word']]
                options.extend(np.random.choice(filtered_words, size=N_OPTIONS - 1, replace=False))
            except ValueError:
                raise ValueError(f'File must contain at least {N_OPTIONS} words')

            flashcard = MultipleChoice(question=definition,
                                       options=options)
            flashcard.entry = entry

            flashcards.append(flashcard)

        return flashcards
