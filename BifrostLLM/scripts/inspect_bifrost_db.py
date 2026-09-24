import sqlite3
import json

conn = sqlite3.connect("bifrost_config.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("TABLES:", tables)

for table in tables:
    cur.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cur.fetchall()]
    cur.execute(f"SELECT * FROM {table} LIMIT 3")
    rows = cur.fetchall()
    if rows:
        print(f"\n--- {table} cols={cols}")
        for row in rows:
            print(row)

conn.close()
