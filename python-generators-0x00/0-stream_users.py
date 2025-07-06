#!/usr/bin/python3

import mysql.connector
from mysql.connector import Error

def stream_users():
    """
    Generator that streams user rows one at a time from user_data table.
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

        for row in cursor:
            yield row  # YIELD one row at a time

        cursor.close()
        connection.close()

    except Error as e:
        print(f"Database error: {e}")
        return
