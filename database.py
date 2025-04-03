"""
Database Module

Handles SQLite operations for the Expense Tracker application.
"""

import sqlite3
import logging
from typing import List, Tuple, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')


class Database:
    def __init__(self) -> None:
        """Initialize the database connection and create the expenses table if it does not exist."""
        try:
            self.conn: Optional[sqlite3.Connection] = sqlite3.connect("expense_tracker.db")
            self.cursor = self.conn.cursor()
            self._create_expenses_table()
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("Database connection error: %s", e)
            self.conn = None

    def _create_expenses_table(self) -> None:
        """
        Create the expenses table with necessary columns if it does not exist.
        """
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                amount REAL,
                category TEXT,
                description TEXT,
                receipt_path TEXT DEFAULT '',
                tags TEXT DEFAULT ''
            )
        '''
        self.cursor.execute(create_table_query)

    def insert_expense(
        self,
        date: str,
        amount: float,
        category: str,
        description: str,
        receipt_path: str = "",
        tags: str = ""
    ) -> bool:
        """Insert a new expense record into the database."""
        try:
            amount_in_inr = self.convert_to_inr(amount)
            query = """
                INSERT INTO expenses (date, amount, category, description, receipt_path, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (date, amount_in_inr, category, description, receipt_path, tags))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error("Insert error: %s", e)
            return False

    def get_expenses(self) -> List[Tuple[Any, ...]]:
        """Retrieve all expense records from the database."""
        try:
            self.cursor.execute("SELECT id, date, amount, category, description FROM expenses")
            expenses = self.cursor.fetchall()
            # Convert the amount to INR format (if necessary)
            expenses_in_inr = [
                (expense[0], expense[1], self.convert_to_inr(expense[2]), expense[3], expense[4])
                for expense in expenses
            ]
            return expenses_in_inr
        except sqlite3.Error as e:
            logging.error("Get expenses error: %s", e)
            return []

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense record by its ID."""
        try:
            self.cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error("Delete error: %s", e)
            return False

    def update_expense(
        self,
        expense_id: int,
        date: str,
        amount: float,
        category: str,
        description: str
    ) -> bool:
        
        try:
            amount_in_inr = self.convert_to_inr(amount)
            query = """
                UPDATE expenses
                SET date = ?, amount = ?, category = ?, description = ?
                WHERE id = ?
            """
            self.cursor.execute(query, (date, amount_in_inr, category, description, expense_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error("Update error: %s", e)
            return False

    def convert_to_inr(self, amount: float) -> float:
        conversion_rate = 1.0  # Default conversion rate; adjust if needed.
        return round(amount * conversion_rate, 2)

    def __del__(self) -> None:
        if self.conn:
            self.conn.close()
