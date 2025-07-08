import sqlite3

class DatabaseConnection:
    """A context manager for managing SQLite database connections."""

    """Initializes the DatabaseConnection with the database name."""
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
    """The begining of the 'with' block to open the database connection."""
    def __enter__(self):
        print("Opening database connection...")
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor
    """The end of the 'with' block to close the database connection."""
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing database connection...")
        if self.conn:
            self.conn.commit()
            self.conn.close()

# ==== Usage ====

with DatabaseConnection('example.db') as cursor:
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    for row in results:
        print(row)
