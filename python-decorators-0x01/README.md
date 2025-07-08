### Python Decorators.

A **decorator** is function that wraps another function to extend or alter its behaviour without modifying the function itself.

At its core:
```python
def decorator(func):
    def wrapper(*arg, **kwargs):
        # Do something Before
        result = func(*arg, **kwargs)
        # Do something After
        result result
    return wrapper
```

You apply like this:
```python
@decorator
def my_func():
```

---

#### Task 0: Logging Database Database Queries

The main aim in this task is to:
* Intercept the function before it runs.
* Log the query passed into the function.
* Then let the function continue as usual.

The `fetch_all_user` function accepts a query string as a parameter. The decorator must extract that and print it before allowing the function to run.

`@log_queries` applies the decorator to `fetch_all_users`. When the `fetch_all_users(query="...")` is called, the `wrapper` function runs first. It grabs the query from `kwargs` or `args`, logs the query, then it call the original function `(func(*args, **kwargs))`

---

#### Task 1: Handle the Database Functions with a Decorator

We are creating a `with_db_connection` that;
    * __Opens__ the SQLite Database connection.
    * __Passes__ the connection(`conn`) as the first argument to the decorated function.
    * __Closes__ the connection after the function completes. Whether it fails or succeeds.

`@with_db_connection` wraps the `get_user_by_id()` so that everytime its called, the decorator handles the db connection and teardown. Wrapper means its an inner function inside the main function.

* Inside `with_db_connecion`
    * `conn = sqlite3.connect('users.db')` opens database connection to `users.db`.
    * `result func(conn, *args, **kwargs)` passes this connection as the first argument to the orginal function `get_user_by_id`.
    * `finally:conn.close()` ensures the connection is closed safely.

The `get_user_by_id()` now expects the first parameter to be a `conn` object. It creates a cursor,runs SQL query with parameter substitution (`?`), and fetches a single result `fetchone`.

__Usage__:

* When you call:
    ```python
    user = get_user_by_id(user_id=1)
    ```
    Python call the `wrapper()` function instead, which:
        * Opens the connection,
        * Calls `get_user_by_id(conn, user_id)`,
        * Closes the connection afterward.

---

#### Task 2: Transaction Management Decorator

Here the decorator chain order goes as follows.
* `@transactional` wraps the actual logic.
* `@with_db_connection` wraps the outermost call.

Like this: 
```python
update_user_email(...) 
→ with_db_connection(wrapper(...))
    → transactional(wrapper(...))
        → update_user_email(conn, user_id, new_email)
```

* `@transactional` receives the connection `conn` from `@with_db_connection`, runs the function `update_user_email(...)`. If successful, its calls `conn.commit()` to persist changes. If an error occurs, calls `conn.rollback()` to revert changes.

* `update_user_email` executes the `UPDATE`query to change user's email.

---

#### Task 3: Using Decorators to Retry Database Queries.

* `retry_on_failure(retries=3, delay=1)` returns a decorator with a specified number of retries and delay. The inner wrapper in it tries to execute the function. If it fails, logs the error, waits delay seconds and tries again. After all the trials fail, it raises the __last caught exception__.

Flow:
* Call `fetch_users_with_retry()`,
* `with_db_connection` opens the database,
* Passes `conn` to `retry_on_failure` which,
    * Tries the operation.
    * Retries on failure.
    * Gves up after max attempts.
* Then connection is closed.

---

#### Task 4: Using Decorators to Cache Database Queries.

* `query_cache = {}` is a simple in-memory dictionary that stores query strings as keys and their result as values.

* `cache_query` wraps the actual query execution. Tries to extract the SQL query string from:
    * `kwargs['query']`, or
    *  `args[1]` (since `arg[0]` is `conn`)

If the query exists in the `query_cache`, returns the cache result. If not, calls the actual DB function, caches its resul and returns it.

* `fetch_user_with_cache(conn, query)` executes `SELECT * FROM users` using DB cursor. Its wrapped with both decorators to use DB connection and cache the result.

