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
                db.insert_transl(lexemes[1], lexemes[2:])
                print(f"db.insert_transl({lexemes[1]}, {lexemes[2:]})")
            case "ers":
                db.erase_transl(lexemes[1], lexemes[2:])
                print(f"db.erase_transl({lexemes[1]}, {lexemes[2:]})")
            case "rep":
                db.erase_transl(lexemes[1], [lexemes[2]])
                print(f"db.erase_transl({lexemes[1]}, {[lexemes[2]]})")
                db.insert_transl(lexemes[1], [lexemes[3]])
                print(f"db.insert_transl({lexemes[1]}, {[lexemes[3]]})")
            case "help":
                print(
                    f"trn - translate(word){linesep}"
                    f"ins - insert(word, [translations]){linesep}"
                    f"ers - erase(word, [translations]){linesep}"
                    f"rep - replace(word, [translations1], [translations2]){linesep}"
                    f"end - end")
            case "end":
                break
    except Exception as e:
        print(e)
