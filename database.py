import sqlite3
import bcrypt

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password BLOB,
        role TEXT
    )
    """)

    # INTERVIEWS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS interviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        score INTEGER,
        feedback TEXT,
        recording TEXT
    )
    """)

    # PROBLEMS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS problems(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )
    """)

    # TEST CASES TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS testcases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id INTEGER,
        input TEXT,
        output TEXT
    )
    """)

    # SUBMISSIONS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        problem_id INTEGER,
        code TEXT,
        result TEXT,
        score INTEGER
    )
    """)

    # DEFAULT ADMIN CREATION
    cur.execute("SELECT * FROM users WHERE email=?", ("admin@gmail.com",))
    admin = cur.fetchone()

    if not admin:

        hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())

        cur.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
        """, ("Admin", "admin@gmail.com", hashed, "admin"))

    conn.commit()
    conn.close()