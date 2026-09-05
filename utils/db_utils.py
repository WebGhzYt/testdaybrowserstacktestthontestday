"""
Database Utility for Syncing Test Execution Results
Supports PostgreSQL with an automatic SQLite fallback for resilience.
"""

import logging
import sqlite3
from datetime import datetime
from utils.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    REPORTS_DIR,
)

logger = logging.getLogger(__name__)

# Track active DB backend
_USE_SQLITE = False
SQLITE_DB_PATH = REPORTS_DIR / "test_execution_results.db"


def _get_pg_connection():
    """Attempt connecting to PostgreSQL."""
    import psycopg2
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=3,
    )


def _get_sqlite_connection():
    """Fallback to local SQLite database."""
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the database table `test_execution_results`.
    Attempts PostgreSQL first, automatically falls back to SQLite if PostgreSQL fails.
    """
    global _USE_SQLITE
    try:
        conn = _get_pg_connection()
        cur = conn.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS test_execution_results (
            id SERIAL PRIMARY KEY,
            test_name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            status VARCHAR(50) NOT NULL,
            duration_seconds NUMERIC(10, 3),
            error_message TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            browser_info VARCHAR(255),
            session_id VARCHAR(255)
        );
        """
        cur.execute(create_table_sql)
        conn.commit()
        cur.close()
        conn.close()
        _USE_SQLITE = False
        logger.info("[DB] Initialized PostgreSQL table `test_execution_results` successfully.")
        return "PostgreSQL"
    except Exception as e:
        logger.warning(
            f"[DB] PostgreSQL connection failed ({e}). Falling back to local SQLite at {SQLITE_DB_PATH}"
        )
        _USE_SQLITE = True
        conn = _get_sqlite_connection()
        cur = conn.cursor()
        create_sqlite_table = """
        CREATE TABLE IF NOT EXISTS test_execution_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            category TEXT,
            status TEXT NOT NULL,
            duration_seconds REAL,
            error_message TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            browser_info TEXT,
            session_id TEXT
        );
        """
        cur.execute(create_sqlite_table)
        conn.commit()
        cur.close()
        conn.close()
        logger.info("[DB] Initialized SQLite table `test_execution_results` successfully.")
        return "SQLite"


def log_test_result(
    test_name: str,
    category: str,
    status: str,
    duration_seconds: float,
    error_message: str = None,
    browser_info: str = "Chrome",
    session_id: str = "LocalSession",
):
    """
    Logs a test case execution outcome into the database.
    """
    global _USE_SQLITE
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not _USE_SQLITE:
        try:
            conn = _get_pg_connection()
            cur = conn.cursor()
            insert_sql = """
            INSERT INTO test_execution_results 
            (test_name, category, status, duration_seconds, error_message, executed_at, browser_info, session_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            cur.execute(
                insert_sql,
                (
                    test_name,
                    category,
                    status,
                    round(duration_seconds, 3),
                    error_message,
                    timestamp,
                    browser_info,
                    session_id,
                ),
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logger.warning(f"[DB] PostgreSQL insert failed: {e}. Switching to SQLite fallback.")
            _USE_SQLITE = True

    # Fallback to SQLite
    try:
        conn = _get_sqlite_connection()
        cur = conn.cursor()
        insert_sqlite = """
        INSERT INTO test_execution_results 
        (test_name, category, status, duration_seconds, error_message, executed_at, browser_info, session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        cur.execute(
            insert_sqlite,
            (
                test_name,
                category,
                status,
                round(duration_seconds, 3),
                error_message,
                timestamp,
                browser_info,
                session_id,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"[DB] Failed to insert result in SQLite: {e}")
        return False


def get_all_results():
    """
    Fetches all execution records from database as a list of dicts.
    """
    global _USE_SQLITE
    records = []

    if not _USE_SQLITE:
        try:
            conn = _get_pg_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, test_name, category, status, duration_seconds, error_message, executed_at, browser_info, session_id 
                FROM test_execution_results 
                ORDER BY id ASC;
                """
            )
            rows = cur.fetchall()
            for r in rows:
                records.append({
                    "id": r[0],
                    "test_name": r[1],
                    "category": r[2],
                    "status": r[3],
                    "duration_seconds": float(r[4]) if r[4] is not None else 0.0,
                    "error_message": r[5] or "",
                    "executed_at": str(r[6]),
                    "browser_info": r[7] or "",
                    "session_id": r[8] or "",
                })
            cur.close()
            conn.close()
            return records
        except Exception as e:
            logger.warning(f"[DB] PostgreSQL read failed: {e}. Reading from SQLite fallback.")
            _USE_SQLITE = True

    # SQLite
    try:
        conn = _get_sqlite_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, test_name, category, status, duration_seconds, error_message, executed_at, browser_info, session_id 
            FROM test_execution_results 
            ORDER BY id ASC;
            """
        )
        rows = cur.fetchall()
        for r in rows:
            records.append({
                "id": r["id"],
                "test_name": r["test_name"],
                "category": r["category"],
                "status": r["status"],
                "duration_seconds": float(r["duration_seconds"]) if r["duration_seconds"] is not None else 0.0,
                "error_message": r["error_message"] or "",
                "executed_at": str(r["executed_at"]),
                "browser_info": r["browser_info"] or "",
                "session_id": r["session_id"] or "",
            })
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"[DB] Failed to read from SQLite: {e}")

    return records
