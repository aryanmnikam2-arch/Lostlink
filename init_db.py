"""
init_db.py  –  Run once to create the SQLite database and tables.
Usage:  python init_db.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "lost_found.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT    NOT NULL UNIQUE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS found_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    item_name       TEXT    NOT NULL,
    description     TEXT    NOT NULL,
    location_found  TEXT    NOT NULL,
    time_found      TEXT    NOT NULL,
    contact_details TEXT    NOT NULL,
    image_path      TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'UNCLAIMED',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

def init():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"[OK] Database initialised at: {DB_PATH}")

if __name__ == "__main__":
    init()
