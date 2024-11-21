import sqlite3


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        user_name TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        card_data TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profile (
        user_id INTEGER PRIMARY KEY,
        total_profit REAL DEFAULT 0,
        profit_count INTEGER DEFAULT 0,
        daily_profit REAL DEFAULT 0,
        monthly_profit REAL DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, user_name):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_exists = cursor.fetchone()

    if user_exists:
        cursor.execute("UPDATE users SET user_name = ? WHERE user_id = ?", (user_name, user_id))
    else:
        cursor.execute("INSERT INTO users (user_id, user_name) VALUES (?, ?)", (user_id, user_name))

    cursor.execute("SELECT * FROM profile WHERE user_id = ?", (user_id,))
    profile_exists = cursor.fetchone()

    if not profile_exists:
        cursor.execute("""
            INSERT INTO profile (user_id, total_profit, profit_count, daily_profit, monthly_profit)
            VALUES (?, 0, 0, 0, 0)
        """, (user_id,))

    conn.commit()
    conn.close()


def get_user_name(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_name FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Пользователь"

def save_card_data(user_id, card_data):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO cards (user_id, card_data) VALUES (?, ?)", (user_id, card_data))
    conn.commit()
    conn.close()

def get_card_data(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT card_data FROM cards WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_profile_data(user_id, total_profit, profit_count, daily_profit, monthly_profit):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO profile (user_id, total_profit, profit_count, daily_profit, monthly_profit)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, total_profit, profit_count, daily_profit, monthly_profit))
    conn.commit()
    conn.close()

def get_profile_data(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT total_profit, profit_count, daily_profit, monthly_profit
    FROM profile WHERE user_id = ?
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "total_profit": result[0],
            "profit_count": result[1],
            "daily_profit": result[2],
            "monthly_profit": result[3]
        }
    else:
        return {
            "total_profit": 0,
            "profit_count": 0,
            "daily_profit": 0,
            "monthly_profit": 0
        }
