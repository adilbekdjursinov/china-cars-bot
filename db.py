import os
import sqlite3

from config import DB_PATH


def _connect() -> sqlite3.Connection:
    folder = os.path.dirname(DB_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                username TEXT,
                car TEXT,
                vin TEXT,
                part TEXT,
                name TEXT,
                phone TEXT,
                city TEXT,
                comment TEXT,
                photo_id TEXT,
                status TEXT DEFAULT 'new'
            )"""
        )


def save_order(data: dict) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO orders (user_id, username, car, vin, part, name, phone, city, comment, photo_id)
               VALUES (:user_id, :username, :car, :vin, :part, :name, :phone, :city, :comment, :photo_id)""",
            data,
        )
        return cur.lastrowid
