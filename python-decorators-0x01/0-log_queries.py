import sqlite3
import functools
from datetime import datetime

#### decorator to lof SQL queries

""" Decorator to log SQL queries executed by a function."""

def log_queries(func):
   @functools.wraps(func)
   def wrapper(*args, **kwargs):
      # Check if 'query' is in kwargs or args
      query = None
      # If 'query' is in kwargs, use it; otherwise, check args  
      if 'query' in kwargs:
            query = kwargs['query']
      elif args:
         query = args[0]

      print(f"Executing query: {query}")
      return func(*args, **kwargs)
   return wrapper  

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
