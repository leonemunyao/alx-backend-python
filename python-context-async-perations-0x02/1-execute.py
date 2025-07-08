import sqlite3

class ExecuteQuery:
    """A context manager for executing a query on an SQLite database."""

    """Initializes the ExecuteQuery with the database name, query, and parameters."""
    def __init__(self, db_name, query, params=()):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn = None
        self.cursor = None
        self.result = None

    """The begining of the 'with' block to open the database connection and execute the query."""
    def __enter__(self):
        print("Opening connection and executing query...")
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.result = self.cursor.fetchall()
        return self.result

    """The end of the 'with' block to close the database connection."""
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection...")
        if self.conn:
            self.conn.commit()
            self.conn.close()

# Using the context manager to fetch users older than 25
query = "SELECT * FROM users WHERE age > ?"
params = (25,)

with ExecuteQuery("Alx_prodev.db", query, params) as results:
    for row in results:
        print(row)
