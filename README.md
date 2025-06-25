## Gist
This is console app that helps you learn English words written in Python.
(Can be compiled for particular OS binaries or just be run with Python) 
## Usage
- Run learning loop:
```python
python main.py [-h] [--mode {eng,rus}] [--alpha ALPHA] [--clear_delay CLEAR_DELAY]
               [--randomness_const RANDOMNESS_CONST] [--sample_size SAMPLE_SIZE]
```
options:
  -h, --help            show this help message and exit
  
  --mode {eng,rus}      Mode of operation: 'eng' or 'rus' (default: eng)
  
  --alpha ALPHA         Alpha value that is using in expovariate distribution (default: 8.0)
  
  --clear_delay CLEAR_DELAY
                        Terminal clear delay in seconds (default: 1.0)
  
  --randomness_const RANDOMNESS_CONST
                        Randomness constant between 0 and 1 (default: 1.0)
  
  --sample_size SAMPLE_SIZE
                        Sample size for each session (default: 50)

- Alter database:
```python
python edit.py
```
options:

trn>word              translate(word)

ins>word>trn1>trn2... insert(word, [translations])

ers>word>trn1>trn2... erase(word, [translations])

del>word              delete(word)

rep>word>trn1>trn2    replace(word, translations1, translations2)

src>word              search_word(word)

end                   end