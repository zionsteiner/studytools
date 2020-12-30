from PyDictionary import PyDictionary
from nltk.stem import WordNetLemmatizer
import argparse
import nltk
nltk.download('wordnet')

def build_dict(args):
    dictionary = PyDictionary()
    lemmatizer = WordNetLemmatizer() 

    src_path = args.src
    dest_path = args.dest if args.dest else src_path

    words = []
    entries = []
    with open(src_path, 'r') as src_file:
        words = [word.replace('\n', '').lower() for word in src_file.readlines()]
        entries = [build_entry(word, lemmatizer, dictionary) for word in words]
    
    with open(dest_path, 'w') as dest_file:
        dest_file.seek(0)
        dest_file.truncate()

        for entry in entries:
            write_entry(entry,  dest_file)

def build_entry(word, lemmatizer, dictionary):
    entry = {'word': word}

    lemma = lemmatizer.lemmatize(entry['word'])
    entry['lemma'] = lemma

    entry['definition'] = []
    try:
        definition = dictionary.meaning(lemma)
        for pos, pos_ds in definition.items():
            for pos_d in pos_ds:
                entry['definition'].append(f'{pos} - {pos_d}')

    except AttributeError:
        entry['definition'] = None

    entry['synonym'] = dictionary.synonym(lemma)
    entry['antonym'] = dictionary.antonym(lemma)

    return entry

def write_entry(entry, file):
    for key, value in entry.items():
        file.write(f'{key.capitalize()}:\n')

        if isinstance(value, list):
            for v in value:
                file.write(f'\t{v}\n')
        elif value is None:
            file.write(f'\tMissing {key}\n')
        else:
            file.write(f'\t{value}\n')

    file.write('------------------\n')

def get_args():
    parser = argparse.ArgumentParser(prog='words2dict',
                                     description='Convert a \\n separated list of words to their respective dictionary entries')
         
    parser.add_argument('-src',
                        metavar='SRC_PATH',
                        type=str,
                        help='Path to the file containing the list of words',
                        required=True)

    parser.add_argument('-dest',
                        metavar='DEST_PATH',
                        type=str,
                        help='Path to the file to write dictionary entries. If omitted, SRC_PATH will be used as the default value',
                        required=False)

    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    build_dict(args)
