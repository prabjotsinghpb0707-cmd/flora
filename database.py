import sqlite3
from pathlib import Path
import os
from datetime import date

DB_PATH = Path(os.getenv(
    "FLOARA_DB_PATH",
    str(Path(__file__).parent / "floara.db")
))


def connect():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            kind TEXT NOT NULL CHECK(kind IN ('Income', 'Expense')),
            amount REAL NOT NULL CHECK(amount > 0),
            category TEXT NOT NULL,
            tx_date TEXT NOT NULL,
            note TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            UNIQUE(user_id, month, category),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)


def create_user(name, email, password_hash):
    try:
        with connect() as db:
            cur = db.execute(
                """INSERT INTO users(name, email, password_hash)
                   VALUES (?, ?, ?)""",
                (name.strip(), email.strip().lower(), password_hash)
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def get_user_by_email(email):
    with connect() as db:
        return db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.strip().lower(),)
        ).fetchone()


def get_user(user_id):
    with connect() as db:
        return db.execute(
            """SELECT id, name, email, created_at
               FROM users WHERE id = ?""",
            (user_id,)
        ).fetchone()


def update_password(user_id, password_hash):
    with connect() as db:
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id)
        )


def update_profile(user_id, name):
    with connect() as db:
        db.execute(
            "UPDATE users SET name = ? WHERE id = ?",
            (name.strip(), user_id)
        )


def add_transaction(user_id, kind, amount, category, tx_date, note=""):
    with connect() as db:
        db.execute("""
            INSERT INTO transactions
            (user_id, kind, amount, category, tx_date, note)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id, kind, float(amount), category,
            tx_date, note.strip()
        ))


def update_transaction(user_id, transaction_id, kind, amount,
                       category, tx_date, note=""):
    with connect() as db:
        db.execute("""
            UPDATE transactions
            SET kind = ?, amount = ?, category = ?,
                tx_date = ?, note = ?
            WHERE id = ? AND user_id = ?
        """, (
            kind, float(amount), category, tx_date,
            note.strip(), transaction_id, user_id
        ))


def delete_transaction(user_id, transaction_id):
    with connect() as db:
        db.execute(
            "DELETE FROM transactions WHERE id = ? AND user_id = ?",
            (transaction_id, user_id)
        )


def get_transactions(user_id, kind="All", search=""):
    sql = "SELECT * FROM transactions WHERE user_id = ?"
    params = [user_id]

    if kind in ("Income", "Expense"):
        sql += " AND kind = ?"
        params.append(kind)

    if search.strip():
        term = f"%{search.strip()}%"
        sql += " AND (category LIKE ? OR note LIKE ?)"
        params.extend([term, term])

    sql += " ORDER BY tx_date DESC, id DESC"

    with connect() as db:
        return db.execute(sql, params).fetchall()


def save_budget(user_id, month, category, amount):
    with connect() as db:
        db.execute("""
            INSERT INTO budgets(user_id, month, category, amount)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, month, category)
            DO UPDATE SET amount = excluded.amount
        """, (user_id, month, category, float(amount)))


def delete_budget(user_id, budget_id):
    with connect() as db:
        db.execute(
            "DELETE FROM budgets WHERE id = ? AND user_id = ?",
            (budget_id, user_id)
        )


def get_budgets(user_id, month):
    with connect() as db:
        return db.execute("""
            SELECT * FROM budgets
            WHERE user_id = ? AND month = ?
            ORDER BY category
        """, (user_id, month)).fetchall()


def get_budget_spent(user_id, month, category):
    with connect() as db:
        row = db.execute("""
            SELECT COALESCE(SUM(amount), 0) AS spent
            FROM transactions
            WHERE user_id = ?
              AND kind = 'Expense'
              AND category = ?
              AND substr(tx_date, 1, 7) = ?
        """, (user_id, category, month)).fetchone()
        return float(row["spent"])


def get_dashboard_data(user_id):
    month = date.today().strftime("%Y-%m")

    with connect() as db:
        totals = db.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN kind='Income'
                    THEN amount ELSE 0 END), 0) AS income,
                COALESCE(SUM(CASE WHEN kind='Expense'
                    THEN amount ELSE 0 END), 0) AS expenses,
                COUNT(*) AS count
            FROM transactions
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        monthly = db.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN kind='Income'
                    THEN amount ELSE 0 END), 0) AS income,
                COALESCE(SUM(CASE WHEN kind='Expense'
                    THEN amount ELSE 0 END), 0) AS expenses
            FROM transactions
            WHERE user_id = ? AND substr(tx_date, 1, 7) = ?
        """, (user_id, month)).fetchone()

        recent = db.execute("""
            SELECT * FROM transactions
            WHERE user_id = ?
            ORDER BY tx_date DESC, id DESC LIMIT 6
        """, (user_id,)).fetchall()

        return {
            "income": float(totals["income"]),
            "expenses": float(totals["expenses"]),
            "balance": float(totals["income"] - totals["expenses"]),
            "count": int(totals["count"]),
            "monthly_income": float(monthly["income"]),
            "monthly_expenses": float(monthly["expenses"]),
            "monthly_savings": float(monthly["income"] - monthly["expenses"]),
            "recent": recent,
        }


def get_category_totals(user_id, month=None):
    sql = """
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE user_id = ? AND kind = 'Expense'
    """
    params = [user_id]

    if month:
        sql += " AND substr(tx_date, 1, 7) = ?"
        params.append(month)

    sql += " GROUP BY category ORDER BY total DESC"

    with connect() as db:
        return db.execute(sql, params).fetchall()


def get_monthly_totals(user_id):
    with connect() as db:
        return db.execute("""
            SELECT
                substr(tx_date, 1, 7) AS month,
                SUM(CASE WHEN kind='Income'
                    THEN amount ELSE 0 END) AS income,
                SUM(CASE WHEN kind='Expense'
                    THEN amount ELSE 0 END) AS expenses
            FROM transactions
            WHERE user_id = ?
            GROUP BY substr(tx_date, 1, 7)
            ORDER BY month DESC LIMIT 6
        """, (user_id,)).fetchall()