import sqlite3 
import functools
from datetime import datetime

# Decorator to handle database connection
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')  # Open the database connection
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.rollback()
        finally:
            conn.close() # Close the connection
    return wrapper

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone()
 
#### Fetch user by ID with automatic connection handling 

user = get_user_by_id(user_id=1)
print(user)
