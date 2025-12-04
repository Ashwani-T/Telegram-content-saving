# db.py
import sqlite3
import time

from config import DB_PATH

con = sqlite3.connect(DB_PATH, check_same_thread=False)

cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS forwarded (
    source_chat TEXT,
    msg_id INTEGER,
    forwarded_at INTEGER,
    PRIMARY KEY(source_chat, msg_id)
)
""")
con.commit()

def was_forwarded(chat_id, msg_id):
    cur = con.cursor()
    cur.execute("SELECT 1 FROM forwarded WHERE source_chat=? AND msg_id=?", (str(chat_id), msg_id))
    return cur.fetchone() is not None

def mark_forwarded(chat_id, msg_id):
    cur = con.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO forwarded (source_chat, msg_id, forwarded_at) VALUES (?, ?, ?)",
        (str(chat_id), msg_id, int(time.time()))
    )
    con.commit()
