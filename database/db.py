import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "capex.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS purchase_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE,
            department TEXT,
            requester TEXT,
            item_name TEXT,
            description TEXT,
            quantity INTEGER,
            estimated_cost REAL,
            category TEXT,
            capex_status TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT UNIQUE,
            allocated_amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS budget_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT,
            description TEXT,
            amount REAL,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS budget_exceptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT,
            description TEXT,
            requested_amount REAL,
            available_amount REAL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# PURCHASE REQUESTS

def save_request(data):
    conn = get_connection()

    conn.execute("""
        INSERT INTO purchase_requests (
            request_id, department, requester,
            item_name, description, quantity,
            estimated_cost, category, capex_status, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["request_id"], data["department"],
        data["requester"], data["item_name"],
        data["description"], data["quantity"],
        data["estimated_cost"], data["category"],
        data["capex_status"], "Pending"
    ))

    conn.commit()
    conn.close()


def get_requests():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM purchase_requests ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows


# BUDGET MANAGEMENT

def save_budget(department, amount):
    conn = get_connection()

    conn.execute("""
        INSERT INTO budgets (department, allocated_amount)
        VALUES (?, ?)
        ON CONFLICT(department)
        DO UPDATE SET allocated_amount = excluded.allocated_amount
    """, (department, amount))

    conn.commit()
    conn.close()


def get_budgets():
    conn = get_connection()

    rows = conn.execute("""
        SELECT b.department, b.allocated_amount,
               COALESCE(SUM(t.amount), 0)
        FROM budgets b
        LEFT JOIN budget_transactions t
        ON b.department = t.department
        GROUP BY b.department, b.allocated_amount
    """).fetchall()

    conn.close()
    return rows


def record_expenditure(department, description, amount):
    conn = get_connection()

    conn.execute("""
        INSERT INTO budget_transactions
        (department, description, amount)
        VALUES (?, ?, ?)
    """, (department, description, amount))

    conn.commit()
    conn.close()


def save_budget_exception(department, description, requested, available):
    conn = get_connection()

    conn.execute("""
        INSERT INTO budget_exceptions
        (department, description, requested_amount, available_amount)
        VALUES (?, ?, ?, ?)
    """, (department, description, requested, available))

    conn.commit()
    conn.close()


def get_budget_exceptions():
    conn = get_connection()

    rows = conn.execute("""
        SELECT * FROM budget_exceptions ORDER BY id DESC
    """).fetchall()

    conn.close()
    return rows


def update_exception_status(exception_id, status):
    conn = get_connection()

    conn.execute("""
        UPDATE budget_exceptions
        SET status = ?
        WHERE id = ?
    """, (status, exception_id))

    conn.commit()
    conn.close()