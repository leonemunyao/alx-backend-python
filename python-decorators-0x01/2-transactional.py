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
            print(f"[LOG] An error occurred: {e}")
            conn.rollback()
        finally:
            conn.close() # Close the connection
    return wrapper

# Decorator to handle transactions
def transactional(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = args[0]  # Assuming the first argument is the connection
        try:
            result = func(*args, **kwargs)
            conn.commit() # Commit the transaction if successful    
            print("[LOG] Transaction committed.")
            return result
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
            conn.rollback()
        return None
    return wrapper

@with_db_connection
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
#### Update user's email with automatic transaction handling 

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
