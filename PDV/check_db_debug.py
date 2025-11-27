import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "mandacarutec.db")
print(f"Checking DB at: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    if ('produtos',) in tables or ('produtos',) in [t for t in tables]: # check if products table exists
        print("Table 'produtos' found.")
        cur.execute("PRAGMA table_info(produtos)")
        cols = cur.fetchall()
        print("Columns in 'produtos':")
        for c in cols:
            print(c)
    else:
        print("Table 'produtos' NOT found.")

    conn.close()
    print("Database check complete.")
except Exception as e:
    print(f"Database error: {e}")
