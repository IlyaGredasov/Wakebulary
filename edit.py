from src.backend.db_client import DataBaseClient
from os import linesep

db = DataBaseClient("database.db")

while True:
    try:
        lexemes = list(input().split(">"))
        match lexemes[0]:
            case "trn":
                print(db.translate_word(lexemes[1]))
            case "ins":
                print(f"db.insert_transl({lexemes[1]}, {lexemes[2:]})")
                db.insert_transl(lexemes[1], lexemes[2:])
            case "ers":
                print(f"db.erase_transl({lexemes[1]}, {lexemes[2:]})")
                db.erase_transl(lexemes[1], lexemes[2:])
            case "del":
                print(f"db.erase_transl({lexemes[1]}, {db.translate_word(lexemes[1])})")
                db.erase_transl(lexemes[1], db.translate_word(lexemes[1]))
            case "rep":
                print(f"db.erase_transl({lexemes[1]}, {[lexemes[2]]})")
                db.erase_transl(lexemes[1], [lexemes[2]])
                print(f"db.insert_transl({lexemes[1]}, {[lexemes[3]]})")
                db.insert_transl(lexemes[1], [lexemes[3]])
            case "help":
                print(
                    f"trn>word - translate(word){linesep}"
                    f"ins>word>trn1>trn2... - insert(word, [translations]){linesep}"
                    f"ers>word>trn1>trn2... - erase(word, [translations]){linesep}"
                    f"del>word - delete(word) {linesep}"
                    f"rep>word>trn1>trn2 - replace(word, translations1, translations2){linesep}"
                    f"end - end")
            case "end":
                break
    except Exception as e:
        print(e)
