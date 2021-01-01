from enum import Enum, auto
from typing import Callable, Any
import numpy
from itertools import count
from words2dict import build_entry
from PyDictionary import PyDictionary
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('wordnet')

class MultipleChoice:
    def __init__(self, question=None, options=None, answer_index=0):
        self.set_question(question)
        self.set_options(options, answer_index)

    def set_question(self, question):
        self.question = question

    def set_options(self, options, answer_index=0):
        self.options = options
        self.answer_index = answer_index
        
    def prompt_user():
        curr_index = count(1)
        prompt_str = 'Select an answer:\n' + '\n'.join([f'{curr_index}:\t{option}' for option in self.options])
        
        print(question)
        user_answer = input(prompt_str)
        valid_input = 1 <= user_answer <= len(options)
        while not valid_input:
            print('Invalid input, try again')
            user_answer = input(prompt_str)
            valid_input = 1 <= user_answer <= len(options)

class Tool:
    def run(self, args):
        pass

class VocabTool(Tool):
    def __init__(self):
        self.dictionary = PyDictionary()
        self.lemmatizer = WordNetLemmatizer()
    
    def run(self, args):
        n_cards = args['count']
        words_path = args['path']
        
        with open(words_path, 'r') as file:
            words = [word.strip().replace('\n', '').lower() for word in file.readlines()]
            word_entries = [build_entry(word, self.lemmatizer, self.dictionary) for word]
            

class ToolID(Enum):
    VOCAB = auto()

class Option:
    def __init__(self, name: str, prompt: str, selection=None, validator: Callable[[..., Any] bool]=None):
        self.name = name
        self.prompt = prompt
        self.validator = validator if validator else (lambda x: return True)
        
        self.__selection = None
        self.selection = selection
        
    @property
    def selection():
        return self.__selection
    
    @selection.setter
    def selection(value):
        if self.validator(value):
            self.__selection = value
        else:
            raise ValueError()
            
    def prompt_user():
        validated = False
        while not validated:
            try:
                self.selection = input(self.prompt)
                validated = True
            except ValueError:
                print('Invalid option, try again')
    

def options_prompt():
    args = {}

    tool_names = {ToolID.VOCAB: 'Vocab Flashcards'}
    tool_options = {ToolID.VOCAB: [Option('path', 'What word file would you like to use?\nEx. words.txt', validator=lambda x: return isinstance(x, str)),
                                   Option('count', 'How many flashcards to go through?', validator=lambda x: return x > 0)]
                    ,}

    tool_id_prompt = 'Select an option:\n' + '\n'.join([f'{tool_id.value}:\t{tool_name}' for tool_id, tool_name in tool_names.items()])
    tool_id_validator = lambda x, max_val=len(tool_ids): return not (1 <= x <= max_val)
    tool_id_option = Option(tool_prompt_str, validator=tool_id_validator)
    tool_id_option.get_selection()

    tool_id = tool_id_option.selection
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
    
    tool.run()
