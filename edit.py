from sys import argv
from db_client import DataBaseClient
from os import linesep

db = DataBaseClient(argv[1])
tables = db.cursor.execute("SELECT name FROM sqlite_master").fetchall()
if not tables:
    db.init_db()

while True:
    try:
        lexemes = list(input().split(">"))
        match lexemes[0]:
            case "map":
                print(db.map_word(lexemes[1]))
            case "ins":
                print(f"db.insert_mapping({lexemes[1]}, {lexemes[2:]})")
                db.insert_mapping(lexemes[1], lexemes[2:])
            case "ers":
                print(f"db.erase_mapping({lexemes[1]}, {lexemes[2:]})")
                db.erase_mapping(lexemes[1], lexemes[2:])
            case "del":
                print(f"db.erase_mapping({lexemes[1]}, {db.map_word(lexemes[1])})")
                db.erase_mapping(lexemes[1], db.map_word(lexemes[1]))
            case "rep":
                print(f"db.erase_mapping({lexemes[1]}, {[lexemes[2]]})")
                db.erase_mapping(lexemes[1], [lexemes[2]])
                print(f"db.insert_mapping({lexemes[1]}, {[lexemes[3]]})")
                db.insert_mapping(lexemes[1], [lexemes[3]])
            case "help":
                print(
                    f"map>word - map(word){linesep}"
                    f"ins>word>trn1>trn2... - insert(word, [mappings]){linesep}"
                    f"ers>word>trn1>trn2... - erase(word, [mappings]){linesep}"
                    f"del>word - delete(word) {linesep}"
                    f"rep>word>trn1>trn2 - replace(word, [mappings1], [mappings2]){linesep}"
                    f"end - end")
            case "end":
                break
    except Exception as e:
        print(e)
