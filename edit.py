from src.backend.db_client import DataBaseClient

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
            case "src":
                results = db.search_word(lexemes[1])
                for w in results:
                    translations = db.translate_word(w)
                    print(f"{w} - {translations}")
            case "exec":
                sql_query = ">".join(lexemes[1:])
                print(f"Executing SQL: {sql_query}")
                try:
                    result = db.cursor.execute(sql_query)
                    db.connection.commit()
                    if sql_query.strip().upper().startswith('SELECT'):
                        rows = result.fetchall()
                        for row in rows:
                            print(row)
                    else:
                        print(f"Query executed successfully. Rows affected: {result.rowcount}")
                except Exception as sql_error:
                    print(f"SQL Error: {sql_error}")
            case "help":
                print(f"""
options:
trn>word              translate(word)
ins>word>trn1>trn2... insert(word, [translations])
ers>word>trn1>trn2... erase(word, [translations])
del>word              delete(word)
rep>word>trn1>trn2    replace(word, translations1, translations2)
src>word              search word
exec>SQL_QUERY        execute any SQL query
end                   end
                    """)
            case "end":
                break
    except Exception as e:
        print(e)
