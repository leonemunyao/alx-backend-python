#!/usr/bin/python3

import mysql.connector
from mysql.connector import Error

def stream_user_ages():
    """
    Generator that yields user ages one at a time from user_data table.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='alxprodev_user',
            password='@1Suburban.',
            database='ALX_prodev'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")

        for row in cursor:
            yield float(row[0])  # row is a tuple like (age,)

        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error streaming ages: {e}")

def calculate_average_age():
    """
    Calculates and prints the average age using the stream_user_ages generator.
    """
    total = 0
    count = 0
    for age in stream_user_ages():  # ✅ Only one loop used here
        total += age
        count += 1

    if count > 0:
        average = total / count
        print(f"Average age of users: {average:.2f}")
    else:
        print("No users found to calculate average.")
