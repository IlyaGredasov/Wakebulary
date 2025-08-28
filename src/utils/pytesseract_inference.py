import string
from pathlib import Path
from sys import argv

import pytesseract
from PIL import Image

pairs = set()


def extract_pairs(image_path):
    global pairs
    raw_text = pytesseract.image_to_string(Image.open(image_path), lang="eng+rus",
                                           config='--oem 3 --psm 6 -c tessedit_char_blacklist=|!@#$%^&*()_+\'‘’`"')
    raw_text = raw_text.replace('‘', '')
    lines = raw_text.split('\n')
    possible_word = None
    english_word_flag = False
    for line in lines:
        if line:
            if not english_word_flag:
                english_word_flag = all(c in string.ascii_lowercase for c in line.split(' ')[0].lower())
                if english_word_flag:
                    possible_word = line.split(' ')[0]
                continue
            elif possible_word and all(
                    c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ " for
                    c in line):
                pairs.add((possible_word, line.strip()))
            english_word_flag = False


if __name__ == '__main__':
    if len(argv) < 2:
        print('Usage: python pytesseract_inference.py path/to/image | path/to/folder')
        exit(1)
    path = Path(argv[1]).resolve()
    if path.is_file():
        print(f"Running: {path}")
        extract_pairs(path)
    elif path.is_dir():
        files = [_ for _ in path.glob('*')]
        for i, file in enumerate(files):
            print(f"[{i}/{len(files)}] Running: {file}")
            extract_pairs(file)
    for first, second in pairs:
        print(f"ins>{first}>{second}")
