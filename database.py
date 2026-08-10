import sqlite3
from datetime import datetime

DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TEXT,
            balance INTEGER DEFAULT 1000,
            total_won INTEGER DEFAULT 0,
            total_lost INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, registered_at, balance, total_won, total_lost)
        VALUES (?, ?, ?, ?, ?, COALESCE((SELECT balance FROM users WHERE user_id = ?), 1000), COALESCE((SELECT total_won FROM users WHERE user_id = ?), 0), COALESCE((SELECT total_lost FROM users WHERE user_id = ?), 0))
    """, (user_id, username, first_name, last_name, datetime.now().isoformat(), user_id, user_id, user_id))
    conn.commit()
    conn.close()

def is_user_registered(user_id: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_total_users() -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_balance(user_id: int) -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_balance(user_id: int, amount: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def update_stats(user_id: int, won: int = 0, lost: int = 0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if won > 0:
        cursor.execute("UPDATE users SET total_won = total_won + ? WHERE user_id = ?", (won, user_id))
    if lost > 0:
        cursor.execute("UPDATE users SET total_lost = total_lost + ? WHERE user_id = ?", (lost, user_id))
    conn.commit()
    conn.close()