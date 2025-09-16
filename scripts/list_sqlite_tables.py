import sqlite3

con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
rows = cur.fetchall()
for r in rows:
    print(r[0])
con.close()
