from src.backend.db_client import DataBaseClient

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
            case "end":
                break
    except Exception as e:
        print(e)
