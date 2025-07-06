#!/usr/bin/python3

import mysql.connector
from mysql.connector import Error

def paginate_users(page_size, offset):
    """
    Fetches a single page of users starting at the given offset.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='alxprodev_user',
            password='@1Suburban.',
            database='ALX_prodev'
        )
        cursor = connection.cursor()
        query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
        cursor.execute(query, (page_size, offset))
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows
    except Error as e:
        print(f"Error in pagination: {e}")
        return []

def lazy_paginate(page_size):
    """
    Generator that lazily fetches and yields pages of users.
    Only loads the next page when needed.
    """
    offset = 0
    while True:  # This is our single loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
