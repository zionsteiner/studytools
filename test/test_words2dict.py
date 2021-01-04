import pytest
import sys
import os
from PyDictionary import PyDictionary

sys.path.append(os.path.join(os.path.dirname(__file__), '../src/'))

from words2dict import parse_dict, parse_entry, read_words, build_dict, build_entry, write_dict, build_and_write_dict

TEXT_DIR = os.path.join(os.path.dirname(__file__), 'test_text')


class Test_parse:
    def test_read_words(self):
        words = read_words(os.path.join(TEXT_DIR, 'words.txt'))
        assert len(words) == 3
        assert all([isinstance(word, str) for word in words])

    def test_read_words_empty(self):
        words = read_words(os.path.join(TEXT_DIR, 'empty.txt'))
        assert len(words) == 0

    def test_parse_dict_count(self):
        entries = parse_dict(os.path.join(TEXT_DIR, 'dict.txt'))
        assert len(entries) == 3

    def test_parse_dict_count_empty(self):
        entries = parse_dict(os.path.join(TEXT_DIR, 'empty.txt'))
        assert len(entries) == 0

    def test_parse_dict_contents(self):
        entries = parse_dict(os.path.join(TEXT_DIR, 'dict.txt'))
        entry = entries[-1]

        exp_entry = {'word': 'pilloried',
                     'definition': ['Verb - expose to ridicule or public scorn',
                                    'Verb - punish by putting in a pillory'],
                     'synonym': ['exhibit', 'display'],
                     'antonym': ['keep quiet', 'underexpose']}

        assert entry == exp_entry

    def test_parse_entry(self):
        with open(os.path.join(TEXT_DIR, 'entry.txt'), 'r') as file:
            text_entry = file.read()
        entry = parse_entry(text_entry)

        exp_entry = {'word': 'pilloried',
                     'definition': ['Verb - expose to ridicule or public scorn',
                                    'Verb - punish by putting in a pillory',
                                    'Verb - criticize harshly or violently'],
                     'synonym': ['exhibit', 'display', 'expose', 'gibbet'],
                     'antonym': ['keep quiet', 'underexpose', 'overexpose', 'veil', 'wrap']}

        assert entry == exp_entry


class Test_build:
    def test_build_dict(self):
        words = read_words(os.path.join(TEXT_DIR, 'words.txt'))
        entries = build_dict(words)

        assert len(words) == len(entries)

    def test_build_entry(self):
        pydict = PyDictionary()

        word = 'pilloried'
        entry = build_entry(word, pydict)

        exp_entry = {'word': 'pilloried',
                     'definition': ['Verb - expose to ridicule or public scorn',
                                    'Verb - punish by putting in a pillory',
                                    'Verb - criticize harshly or violently'],
                     'synonym': ['exhibit', 'display', 'expose', 'gibbet'],
                     'antonym': ['keep quiet', 'underexpose', 'overexpose', 'veil', 'wrap']}

        assert entry == exp_entry


def test_write():
    exp_entries = [{'word': 'affable',
                    'definition': ['Adjective - diffusing warmth and friendliness'],
                    'synonym': ['cordial', 'genial', 'amiable', 'friendly'],
                    'antonym': ['unfriendly', 'insincere', 'cool', 'inhospitable', 'ill-natured']},
                   {'word': 'pilloried',
                    'definition': ['Verb - expose to ridicule or public scorn',
                                   'Verb - punish by putting in a pillory',
                                   'Verb - criticize harshly or violently'],
                    'synonym': ['exhibit', 'display', 'expose', 'gibbet'],
                    'antonym': ['keep quiet', 'underexpose', 'overexpose', 'veil', 'wrap']}]

    path = os.path.join(TEXT_DIR, 'test_write.txt')
    write_dict(exp_entries, path)
    entries = parse_dict(path)

    with open(path, 'w') as file:
        file.truncate(0)

    assert entries == exp_entries


class Test_build_and_write_dict():
    def test_build_and_write_to_other(self):
        args = {'src': os.path.join(TEXT_DIR, 'words.txt'),
                'dest': os.path.join(TEXT_DIR, 'test_write.txt'),
                'append': False}

        build_and_write_dict(args)

        entries = parse_dict(args['dest'])
        words = read_words(args['src'])

        with open(args['dest'], 'w') as file:
            file.truncate(0)

        assert len(entries) == len(words)

    def test_build_and_write_to_self(self):
        args = {'src': os.path.join(TEXT_DIR, 'self_write.txt'),
                'dest': os.path.join(TEXT_DIR, 'self_write.txt'),
                'append': False}

        with open(args['dest'], 'r') as file:
            self_write = file.read()

        words = read_words(args['src'])

        build_and_write_dict(args)
        entries = parse_dict(args['dest'])

        with open(args['dest'], 'w') as file:
            file.seek(0)
            file.truncate()
            file.write(self_write)

        assert len(entries) == len(words)

    def test_build_and_write_append(self):
        args = {'src': os.path.join(TEXT_DIR, 'words2.txt'),
                'dest': os.path.join(TEXT_DIR, 'dict.txt'),
                'append': True}

        entries_before = parse_dict(args['dest'])

        with open(args['dest'], 'r') as file:
            dict_txt = file.read()

        build_and_write_dict(args)

        words_added = read_words(args['src'])
        entries_after = parse_dict(args['dest'])

        with open(args['dest'], 'w') as file:
            file.seek(0)
            file.truncate()
            file.write(dict_txt)

        assert len(entries_after) == (len(entries_before) + len(words_added))

    def test_build_and_write_append_to_empty(self):
        args = {'src': os.path.join(TEXT_DIR, 'words.txt'),
                'dest': os.path.join(TEXT_DIR, 'empty.txt'),
                'append': True}

        entries_before = parse_dict(args['dest'])
        assert len(entries_before) == 0

        build_and_write_dict(args)

        words = read_words(args['src'])
        entries = parse_dict(args['dest'])

        with open(args['dest'], 'w') as file:
            file.seek(0)
            file.truncate()

        assert len(entries) == len(words)

    def test_build_and_write_append_from_empty(self):
        args = {'src': os.path.join(TEXT_DIR, 'empty.txt'),
                'dest': os.path.join(TEXT_DIR, 'dict.txt'),
                'append': True}

        entries_before = parse_dict(args['dest'])

        with open(args['dest'], 'r') as file:
            dict_txt = file.read()

        build_and_write_dict(args)

        words = read_words(args['src'])
        assert len(words) == 0

        entries_after = parse_dict(args['dest'])

        with open(args['dest'], 'w') as file:
            file.seek(0)
            file.truncate()
            file.write(dict_txt)

        assert len(entries_before) == len(entries_after)
