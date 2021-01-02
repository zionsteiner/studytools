from enum import Enum, auto
from itertools import count
from typing import Callable, Any
import numpy as np
from PyDictionary import PyDictionary

from words2dict import build_dict, write_dict, parse_dict


class MultipleChoice:
    def __init__(self, question: str, options: list = None, answer_index=0):
        self.question = None
        self.set_question(question)
        self.options = None
        self.answer_index = None
        self.set_options(options, answer_index)

    def set_question(self, question: str):
        self.question = question

    def set_options(self, options: list, answer_index=0):
        self.options = options
        self.answer_index = answer_index

        self.shuffle_options()

    def shuffle_options(self):
        new_indices = list(range(len(self.options)))
        np.random.shuffle(new_indices)
        self.options = [self.options[x] for x in new_indices]
        self.answer_index = new_indices.index(self.answer_index)

    def get_user_answer(self):
        curr_index = count(1)
        prompt_str = 'Select an answer:\n' + '\n'.join([f'{next(curr_index)}:\t{option}' for option in self.options])

        print(self.question)
        user_answer = int(input(prompt_str + '\n'))
        print()

        valid_input = 1 <= user_answer <= len(self.options)
        while not valid_input:
            print('Invalid input, try again')
            print(self.question)
            user_answer = int(input(prompt_str + '\n'))
            print()

            valid_input = 1 <= user_answer <= len(self.options)

        if user_answer == (self.answer_index + 1):
            print('Correct!\n')
            return True
        else:
            print(f"Incorrect, the correct answer was '{self.options[self.answer_index]}'\n")
            return False


class Tool:
    def run(self, args):
        pass


class VocabTool(Tool):
    def __init__(self):
        self.dictionary = PyDictionary()

    def run(self, args):
        print('Loading vocab...\n')
        flashcards = self.load_flashcards(path=args['words_path'], is_dict=args['is_dict'], n_words=args['n_cards'])

        play_again = True
        while play_again:
            flashcards = self.show_flashcards(flashcards)
            if len(flashcards):
                play_again_input = int(
                    input('Would you like to play again with the words you missed?\n1.\tYes\n2.\tNo\n'))
                print()

                play_again = True if play_again_input == 1 else False
            else:
                play_again = False

        input('Press enter to exit')

    def show_flashcards(self, flashcards):
        mistakes = []

        print('Flashcards')
        print('----------')
        for flashcard in flashcards:
            flashcard.shuffle_options()
            is_correct = flashcard.get_user_answer()
            if not is_correct:
                mistakes.append(flashcard)

        accuracy = (len(flashcards) - len(mistakes)) / len(flashcards)
        addendum = 'Good job!' if accuracy > 0.5 else 'You have some work to do!'
        print(f'You got {accuracy * 100:.2f}% right. {addendum}\n')

        return mistakes

    def load_flashcards(self, path: str, is_dict: bool, n_words: int):
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
            entries = build_dict(path, n_words, progress_bar=True)
            with open(path, 'r') as file:
                words = sorted(set([word.strip().replace('\n', '').lower() for word in file.readlines()]))

            save_dict_option = Option(name='save_dict',
                                      prompt='Save generated dictionary? You can load vocab from this quicker next time\n1.\tYes\n2.\tNo',
                                      validator=lambda x: 1 <= int(x) <= 2,
                                      processor=lambda x: True if int(x) == 1 else False)
            save_dict_option.prompt_user()

            if save_dict_option.selection:
                save_path_option = Option(name='save_path',
                                          prompt='Enter a path to save the dictionary to')
                save_path_option.prompt_user()
                path = save_path_option.selection
                write_dict(entries, path)

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
            flashcards.append(flashcard)

        return flashcards


class ToolID(Enum):
    VOCAB = auto()


class Option:
    def __init__(self, name: str, prompt: str, selection=None, validator: Callable[[Any], bool] = None,
                 processor: Callable = str):
        self.name = name
        self.prompt = prompt
        self.processor = processor
        if validator:
            self.validator = validator
        else:
            self.validator = lambda x: True

        self.__selection = None

        if selection:
            self.selection = selection

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
                print('Invalid option, try again')


def options_prompt():
    args = {}

    tool_names = {ToolID.VOCAB: 'Vocab Flashcards'}
    tool_options = {ToolID.VOCAB: [
        Option(name='words_path',
               prompt='What word file would you like to use?\nEx. words.txt'),
        Option(name='is_dict',
               prompt='Is this a list of words, or a pregenerated dictionary file?\n1.\tWords\n2.\tDictionary',
               validator=lambda x: 1 <= int(x) <= 2,
               processor=lambda x: bool(int(x) - 1)),
        Option(name='n_cards',
               prompt='How many flashcards to go through?',
               validator=lambda x: int(x) > 0,
               processor=int),
    ],
    }

    tool_id_prompt = 'Select an option:\n' + '\n'.join(
        [f'{tool_id.value}:\t{tool_name}' for tool_id, tool_name in tool_names.items()])
    tool_id_option = Option('tool_id', prompt=tool_id_prompt,
                            validator=lambda x, max_val=len(tool_names): 1 <= int(x) <= max_val,
                            processor=lambda x: ToolID(int(x)))
    tool_id_option.prompt_user()

    args[tool_id_option.name] = tool_id_option.selection

    options = tool_options[tool_id_option.selection]
    for option in options:
        option.prompt_user()
        args[option.name] = option.selection

    return args


def get_tool(tool_id: ToolID):
    tools = {ToolID.VOCAB: VocabTool}

    tool = tools[tool_id]()
    return tool


if __name__ == '__main__':
    args = options_prompt()
    tool = get_tool(args['tool_id'])
    args.pop('tool_id')

    tool.run(args)
