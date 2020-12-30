# ToDo: CLI
# Options:
#   path
#   erase, append, new file

from PyDictionary import PyDictionary
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('wordnet')

d = PyDictionary()
lemmatizer = WordNetLemmatizer() 

file_name = 'C:\\Users\\ender\\OneDrive\\Desktop\\gre_vocab.txt'

with open(file_name, 'r+') as file:
    words = [{'word': word.replace('\n', '').lower()} for word in file.readlines()]

    file.seek(0)
    file.truncate()
    for word in words:
        lemma = lemmatizer.lemmatize(word['word'])
        word['lemma'] = lemma
        print(lemma)
        definitions = d.meaning(lemma)

        word['definition'] = []
        try:
            definition = d.meaning(lemma)
            for pos, pos_ds in definition.items():
                for pos_d in pos_ds:
                    word['definition'].append(f'{pos} - {pos_d}')

        except AttributeError:
            word['definition'] = None

        word['synonym'] = d.synonym(lemma)
        word['antonym'] = d.antonym(lemma)
        
        for key, value in word.items():
            file.write(f'{key.capitalize()}:\n')

            if isinstance(value, list):
                for v in value:
                    file.write(f'\t{v}\n')
            elif value is None:
                file.write(f'\tMissing {key}\n')
            else:
                file.write(f'\t{value}\n')

        file.write('------------------\n')
        