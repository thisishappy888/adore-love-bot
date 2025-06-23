import sqlite3
from aiogram import Router

router = Router()

with sqlite3.connect("database.db") as db:
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            bio TEXT,
            photo_file_id TEXT
        )
    """
    )

    cursor.execute(
        """
                   CREATE TABLE IF NOT EXISTS likes (
                   from_user INTEGER,
                   to_user INTEGER,
                   UNIQUE(from_user, to_user)
                   )
                   """
    )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS dislikes (
        from_user INTEGER,
        to_user INTEGER,
        timestamp DATETIME
        )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS timeouts (
        user_id INTEGER PRIMARY KEY,
        timeout_until DATETIME
    )
    """
    )
