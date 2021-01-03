import argparse
import os
from typing import List, Dict

import numpy as np
from PyDictionary import PyDictionary
from tqdm import tqdm

ENTRY_DELIM = '------------------'


def build_dict(path, n_words=None, progress_bar=False):
    dictionary = PyDictionary()

    words = []
    entries = []
    with open(path, 'r') as file:
        words = sorted(set([word.strip().lower() for word in file.readlines()]))

        if n_words:
            try:
                words = np.random.choice(words, size=n_words, replace=False)
            except ValueError:
                raise ValueError(f'File must contain at least {n_words} words')

        if progress_bar:
            for word in tqdm(words):
                entries.append(build_entry(word, dictionary))
        else:
            entries = [build_entry(word, dictionary) for word in words]

    return entries


def build_entry(word, dictionary):
    entry = {'word': word, 'definition': []}

    try:
        definition = dictionary.meaning(word)
        for pos, pos_defs in definition.items():
            for pos_def in pos_defs:
                entry['definition'].append(f'{pos} - {pos_def}')

    except AttributeError:
        entry['definition'] = None

    entry['synonym'] = dictionary.synonym(word)
    entry['antonym'] = dictionary.antonym(word)

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

    file.write(ENTRY_DELIM+'\n')


def write_dict(entries, path, append=False):
    if append:
        existing_entries = parse_dict(path) if os.path.isfile(path) else []
        new_words = [entry['word'] for entry in entries]
        entries.extend([entry for entry in existing_entries if entry['word'] not in new_words])
        entries.sort(key=lambda entry: entry['word'])

    with open(path, 'w') as file:
        for entry in entries:
            write_entry(entry, file)


def build_and_write_dict(args):
    src_path = args.src
    dest_path = args.dest if args.dest else src_path

    print('Building dict...')
    entries = build_dict(src_path, progress_bar=True)
    print('Writing dict...')
    write_dict(entries, dest_path, args.append)
    print('Done.')


def parse_dict(path: str) -> List[Dict]:
    dict_text = ''
    with open(path, 'r') as file:
        dict_text = file.read()

    text_entries = dict_text.strip().split(ENTRY_DELIM)[:-1]
    entries = [parse_entry(entry) for entry in text_entries]

    return entries


def parse_entry(text_entry: str) -> Dict:
    lines = text_entry.strip().replace('\t', '').split('\n')

    entry = {'word': lines[lines.index('Word:') + 1],
             'definition': lines[lines.index('Definition:') + 1:lines.index('Synonym:')],
             'synonym': lines[lines.index('Synonym:') + 1:lines.index('Antonym:')],
             'antonym': lines[lines.index('Antonym:') + 1:]}

    return entry


def validate_args(args):
    if not os.path.isfile(args.src):
        raise ValueError(f'File {args.src} does not exist')


def get_args():
    parser = argparse.ArgumentParser(prog='words2dict',
                                     description='Convert a \\n separated list of words to their respective dictionary entries')

    parser.add_argument('-src',
                        metavar='SRC_PATH',
                        type=str,
                        required=True,
                        help='Path to the file containing the list of words')

    parser.add_argument('-dest',
                        metavar='DEST_PATH',
                        type=str,
                        required=False,
                        help='Path to the file to write dictionary entries. If omitted, SRC_PATH will be used as the default value')

    parser.add_argument('--append',
                        dest='append',
                        action='store_true',
                        required=False,
                        help='Whether to append to file at DEST_PATH or overwrite')

    args = parser.parse_args()
    validate_args(args)

    return args


if __name__ == '__main__':
    args = get_args()
    build_and_write_dict(args)
