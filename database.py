"""Database access layer for the Employee Performance Evaluation System.

The project uses a local SQLite database so the college demo can run on any
computer without external database setup.
The project prefers Oracle through python-oracledb thin mode. If Oracle settings are
not available, it automatically uses a local SQLite database so the college demo can
run on any laptop without changing application code.
"""

from __future__ import annotations

import logging
import os
import shutil
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_PATH = BASE_DIR / "employee_performance.db"


class DatabaseManager:
    """Centralized database manager used by all GUI modules."""

    def __init__(self) -> None:
        """Create a SQLite database manager for the local demo database."""
        LOGGER.info("Using local SQLite database at %s", SQLITE_DB_PATH)
        """Create a database manager and decide whether Oracle is configured."""
        self.use_oracle = all(
            os.getenv(name) for name in ("ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN")
        )
        self._oracledb: Any | None = None
        if self.use_oracle:
            try:
                import oracledb

                self._oracledb = oracledb
                LOGGER.info("Oracle configuration found. Using Oracle thin mode.")
            except ImportError:
                LOGGER.warning("oracledb is not installed. Falling back to SQLite.")
                self.use_oracle = False
        else:
            LOGGER.info("Oracle environment variables not found. Using SQLite.")

    @contextmanager
    def connect(self) -> Iterator[Any]:
        """Yield a database connection and always close it safely."""
        connection = None
        try:
            connection = sqlite3.connect(SQLITE_DB_PATH)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            if self.use_oracle and self._oracledb is not None:
                connection = self._oracledb.connect(
                    user=os.environ["ORACLE_USER"],
                    password=os.environ["ORACLE_PASSWORD"],
                    dsn=os.environ["ORACLE_DSN"],
                )
            else:
                connection = sqlite3.connect(SQLITE_DB_PATH)
                connection.row_factory = sqlite3.Row
            yield connection
            connection.commit()
        except Exception:
            if connection is not None:
                connection.rollback()
            LOGGER.exception("Database transaction failed")
            raise
        finally:
            if connection is not None:
                connection.close()

    def initialize(self) -> None:
        """Create required tables and seed demonstration data when empty."""
        with self.connect() as conn:
            cursor = conn.cursor()
            self._create_tables(cursor)
            self._seed_data(cursor)

    def _create_tables(self, cursor: Any) -> None:
        """Create tables used by the application."""
        statements = [
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('Admin', 'HR', 'Manager'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                designation TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                joining_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active',
                photo_path TEXT DEFAULT ''
                status TEXT NOT NULL DEFAULT 'Active'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS evaluations (
                evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                period TEXT NOT NULL,
                ratings REAL NOT NULL CHECK (ratings BETWEEN 0 AND 10),
                attendance REAL NOT NULL CHECK (attendance BETWEEN 0 AND 10),
                productivity REAL NOT NULL CHECK (productivity BETWEEN 0 AND 10),
                teamwork REAL NOT NULL CHECK (teamwork BETWEEN 0 AND 10),
                total_score REAL NOT NULL DEFAULT 0,
                grade TEXT NOT NULL DEFAULT 'C',
                suggestion TEXT NOT NULL DEFAULT '',
                remarks TEXT,
                evaluated_on TEXT NOT NULL DEFAULT CURRENT_DATE,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                    ON DELETE CASCADE,
                UNIQUE (employee_id, period)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_name TEXT NOT NULL UNIQUE,
                manager_name TEXT NOT NULL DEFAULT 'Not Assigned'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS designations (
                designation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                designation_name TEXT NOT NULL UNIQUE,
                department_name TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                attendance_date TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('Present', 'Absent', 'Half Day', 'Leave')),
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
                UNIQUE (employee_id, attendance_date)
            )
            """,
        ]
        for statement in statements:
            cursor.execute(statement)
        self._migrate_tables(cursor)

    def _migrate_tables(self, cursor: Any) -> None:
        """Add newer columns when upgrading an existing SQLite demo database."""
        columns = {row[1] for row in cursor.execute("PRAGMA table_info(employees)").fetchall()}
        if "photo_path" not in columns:
            cursor.execute("ALTER TABLE employees ADD COLUMN photo_path TEXT DEFAULT ''")
        eval_columns = {row[1] for row in cursor.execute("PRAGMA table_info(evaluations)").fetchall()}
        for column, definition in {
            "total_score": "REAL NOT NULL DEFAULT 0",
            "grade": "TEXT NOT NULL DEFAULT 'C'",
            "suggestion": "TEXT NOT NULL DEFAULT ''",
        }.items():
            if column not in eval_columns:
                cursor.execute(f"ALTER TABLE evaluations ADD COLUMN {column} {definition}")
        ]
        for statement in statements:
            cursor.execute(statement)

    def _seed_data(self, cursor: Any) -> None:
        """Insert default users and sample employees for a ready demo."""
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                [("admin", "admin123", "Admin"), ("hr", "hr123", "HR"), ("manager", "manager123", "Manager")],
            )
        cursor.execute("SELECT COUNT(*) FROM departments")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO departments (department_name, manager_name) VALUES (?, ?)",
                [("IT", "Neha Rao"), ("HR", "Amit Shah"), ("Finance", "Priya Nair"), ("Sales", "Vikram Singh"), ("Operations", "Meera Joshi")],
            )
        cursor.execute("SELECT COUNT(*) FROM designations")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO designations (designation_name, department_name) VALUES (?, ?)",
                [("Software Engineer", "IT"), ("HR Executive", "HR"), ("Accountant", "Finance"), ("Sales Manager", "Sales"), ("Operations Lead", "Operations")],
            )
        cursor.execute("SELECT COUNT(*) FROM employees")
        if cursor.fetchone()[0] == 0:
            employees = [
                ("Aarav Sharma", "IT", "Software Engineer", "aarav@example.com", "9876543210", "2023-01-10", "Active"),
                ("Diya Patel", "HR", "HR Executive", "diya@example.com", "9876543211", "2022-07-18", "Active"),
                ("Rahul Verma", "Finance", "Accountant", "rahul@example.com", "9876543212", "2021-11-05", "Active"),
                ("Sneha Iyer", "Sales", "Sales Manager", "sneha@example.com", "9876543213", "2020-03-22", "Active"),
                ("Kabir Khan", "Operations", "Operations Lead", "kabir@example.com", "9876543214", "2019-09-14", "Active"),
            ]
            cursor.executemany(
                """
                INSERT INTO employees
                (name, department, designation, email, phone, joining_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                employees,
            )

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        """Return all rows for a query as dictionaries."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        """Return one row for a query as a dictionary."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        """Execute an INSERT, UPDATE, or DELETE statement."""
        with self.connect() as conn:
            conn.cursor().execute(query, params)

    def backup(self, destination: Path) -> Path:
        """Create a SQLite database backup for demonstrations."""
        self.initialize()
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SQLITE_DB_PATH, destination)
        return destination

    def restore(self, source: Path) -> None:
        """Restore the SQLite database from a selected backup file."""
        if not source.exists():
            raise FileNotFoundError(f"Backup file not found: {source}")
        shutil.copy2(source, SQLITE_DB_PATH)


DB = DatabaseManager()
