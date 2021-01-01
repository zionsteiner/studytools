from enum import Enum, auto
from itertools import count
from typing import Callable, Any
import numpy as np
import nltk
from PyDictionary import PyDictionary
from nltk.stem import WordNetLemmatizer

from words2dict import build_dict

nltk.download('wordnet', quiet=True)


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
        user_answer = int(input(prompt_str+'\n'))
        valid_input = 1 <= user_answer <= len(self.options)
        while not valid_input:
            print('Invalid input, try again')
            user_answer = int(input(prompt_str+'\n'))
            valid_input = 1 <= user_answer <= len(self.options)

        if user_answer == (self.answer_index+1):
            print('Correct!')
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
        self.lemmatizer = WordNetLemmatizer()

    def run(self, args):
        print('Loading vocab...')
        flashcards = self.load_flashcards(path=args['words_path'], n_words=args['n_cards'])

        play_again = True
        while play_again:
            flashcards = self.show_flashcards(flashcards)
            if len(flashcards):
                play_again_input = int(input('Would you like to play again with the words you missed?\n1.\tYes\n2.\tNo\n'))
                play_again = True if play_again_input == 1 else False
            else:
                play_again = False

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
        print(f'You got {accuracy*100:.2f}% right. {addendum}')

        return mistakes

    def load_flashcards(self, path: str, n_words: int):
        entries = build_dict(path, n_words, progress_bar=True)
        entries = [entry for entry in entries if entry['definition']]

        words = []
        with open(path, 'r') as file:
            words = [word.strip().replace('\n', '').lower() for word in file.readlines()]

        flashcards = []
        N_OPTIONS = 4
        for entry in entries:
            definition = 'Definition: ' + np.random.choice(entry['definition']).split(' - ')[1]
            options = [entry['lemma']]

            try:
                filtered_words = [word for word in words if word != entry['lemma']]
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
    def __init__(self, name: str, prompt: str, selection=None, validator: Callable[[Any], bool] = None, cast_type: type = str):
        self.name = name
        self.prompt = prompt
        self.cast_type = cast_type
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
            self.__selection = value
        else:
            raise ValueError()

    def prompt_user(self):
        validated = False
        while not validated:
            try:
                self.selection = self.cast_type(input(self.prompt+'\n'))
                print()
                validated = True
            except ValueError:
                print('Invalid option, try again')


def options_prompt():
    args = {}

    tool_names = {ToolID.VOCAB: 'Vocab Flashcards'}
    tool_options = {ToolID.VOCAB: [
        Option('words_path', 'What word file would you like to use?\nEx. words.txt', validator=lambda x: isinstance(x, str), cast_type=str),
        Option('n_cards', 'How many flashcards to go through?', validator=lambda x: x > 0, cast_type=int)],
    }

    tool_id_prompt = 'Select an option:\n' + '\n'.join(
        [f'{tool_id.value}:\t{tool_name}' for tool_id, tool_name in tool_names.items()])
    tool_id_option = Option('tool_id', prompt=tool_id_prompt,
                            validator=lambda x, max_val=len(tool_names): 1 <= x <= max_val,
                            cast_type=int)
    tool_id_option.prompt_user()

    tool_id = ToolID(tool_id_option.selection)
    args[tool_id_option.name] = tool_id

    options = tool_options[tool_id]
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
