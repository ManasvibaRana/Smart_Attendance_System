"""Tiny SQLite student database. photo_name must match the photo's file name in photosss/."""
import sqlite3
from contextlib import closing

DB_FILE = "students.db"


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            photo_name TEXT PRIMARY KEY COLLATE NOCASE,
            full_name  TEXT NOT NULL,
            roll_no    TEXT,
            branch     TEXT,
            semester   INTEGER
        )
    """)
    return conn


def add_student(photo_name, full_name, roll_no, branch, semester):
    with closing(connect()) as conn, conn:
        conn.execute(
            "INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?, ?)",
            (photo_name, full_name, roll_no, branch, semester),
        )


def get_all_students():
    """Return {photo_name (lower-case): row dict} so lookups don't hit the DB every frame."""
    with closing(connect()) as conn:
        rows = conn.execute("SELECT * FROM students").fetchall()
    return {row["photo_name"].lower(): dict(row) for row in rows}
