# Study Tools
This is a collection of tools to help me study for the GRE.

### Tools:
#### Vocab Flashcards
Requires a list of vocab words saved to a file, like the **words.txt** example below. Each word must be on its own line.
It also accepts a pregenerated dictionary file like **dictionary.txt**.

The tools loads the word definitions and displays multiple choice prompts:
```
Definition: the deliberate act of deviating from the truth
Select an answer:
1:	bucolic
2:	discomfiting
3:	prevarication
4:	recrudescent
```

#### Comprehension (ToDo)
#### Fill in the blank (ToDo)
#### Quantitative (ToDo)

### Usage
```
python studytools.py
```

Alternatively, download and run a release
#### Windows
```
studytools.exe
```
#### Linux
```
./studytools
```

### Requirements
If you run this as a Python script and not a release, you'll need to download the dependencies.
Run the following terminal command to install the modules you need:
```
pip install -r requirements.txt
```

## words2dict
This script converts a newline delimited list of words to their dictionary entries. It also contains utility functions
used in `studytools.py`.

### Example Usage
words.txt
```
dinosaur
rampant
```

Command
```
python words2dict.py -src words.txt -dest dictionary.txt
```

dictionary.txt
```
Word:
    dinosaur
Definition:
    Noun - any of numerous extinct terrestrial reptiles of the Mesozoic era
Synonym:
    argentinosaur
Antonym:
    anapsid
------------------
Word:
    rampant
Definition:
    Adjective - unrestrained and violent
    Adjective - rearing on left hind leg with forelegs elevated and head usually in profile
Synonym:
    uncontrolled
Antonym:
    controlled
    level
------------------
```