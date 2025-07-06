#!/usr/bin/python3

import mysql.connector
from mysql.connector import Error


def stream_users_in_batches(batch_size):
    """
    Generator that yields batches of rows from user_data.
    Each batch is a list of rows (tuples).
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='alxprodev_user',
            password='@1Suburban.',
            database='ALX_prodev'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data")

        batch = []
        for row in cursor:
            batch.append(row)
            if len(batch) == batch_size:
                yield batch
                batch = []  # Reset for next batch

        # Yield the final batch if not empty
        if batch:
            yield batch

        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error fetching batches: {e}")
        return


def batch_processing(batch_size):
    """
    Processes batches to filter users over the age of 25.
    Yields individual users (rows) from each batch who meet the condition.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if float(user[3]) > 25:  # age is the 4th column
                yield user
