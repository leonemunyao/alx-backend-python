## Context Managers and Asynchronous programming in Python

#### Task 0: Custom Class Based Context Manager for Database Connection.

* `__init__(self, db_name)` initiliazes the class with the name of the database to connect to.
* `__enter__(self)` This opens a connection and returns the cursor so that the queries inside the `with` block are executed.

* `__exit__(self, exc_type, exc_val, exc_tb)` This is called when the `with` block is exited. Ensures connection is committed and closed.

When you run:
```python
with DatabaseConnection('ALX_prodev.db') as cursor:
    cursor.execute("SELECT * FROM users")
    ...
```
Python internally does the following:
    * Calls `DatabaseConnection('ALX_prodev')`, initiliazes the object.
    * Calls `__enter__()`, opens the connection, gets the cursor, assigns it to `cursor`.
    * Executes the block of code inside `with`.
    * After the block(or if an exception occurs), it calls `__exit__()`, commits and closes the connection.

---

#### Task 1: Reusable Query Context Manager.

What happened;
```python
with ExecuteQuery("ALX_prodev.db", query, params) as results:
```
* `ExecuteQuery()` initiliazes the object.
* `__enter__()` is called;
    * Connects the database.
    * Executes the query with parameter `25`.
    * Stores and returns the result `fetchall`
* When the block ends, `__exit__()` is called, commits and closes the connection.

---

#### Task 2: Concurrent Asynchronous Database Queries.

The task aims at showing how to run multiple database queries concurrently using `asyncio.gather` and the `aiosqlite` library for aynchronous interaction with SQLite.

* `aiosqlite.connect(...)` opens asynchronous connection to the SQLite Database.
* `async with ...` ensures context is manageg properly(i.e autclose and exit).
* `await cursor.fetchall(...)` asynchrounously retrieves all the results from the cursor.
* `asyncio.gather(...)` runs multiple async functions concurrently.
* `asyncio.run(...)` starts the event loop and runs the `fetch_concurrently()` coroutine.


