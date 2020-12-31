# words2dict
This script converts a newline delimited list of words to their dictionary entries.


### Requirements
Run the following terminal command to install dependencies:
```
pip install -r requirements.txt
```

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
Lemma:
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
Lemma:
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