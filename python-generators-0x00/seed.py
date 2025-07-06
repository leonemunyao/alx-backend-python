#!/usr/bin/python3

import os
import csv
import uuid
import mysql.connector
from mysql.connector import Error

def connect_db():
    """ Connect to MySQL database """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='alxprodev_user',
            password='@1Suburban.'
        )
        return connection
    except Error as e:
        print(f"Erro Connecting to MySQL: {e}")
        return None
def create_database(connection):
    """Creates the ALX_prodev database if it does not exist."""

    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created successfully.")
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()

def connect_to_prodev():
    """ Connect to the ALX_prodev database """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='alxprodev_user',
            password='@1Suburban.',
            database='ALX_prodev'
        )
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None
    
def create_table(connection):
    """Creates the user_data table in the ALX_prodev database."""
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        print("Table user_data created successfully")
    except Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, filename):
    """Inserts data from CSV into the user_data table if not already inserted."""
    try:
        cursor = connection.cursor()
        inserted_count = 0
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                query = """
                INSERT IGNORE INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    str(uuid.uuid4()),  # Generate a unique UUID for user_id
                    row['name'],
                    row['email'],
                    row['age']
                ))
                inserted_count += 1
        connection.commit()
        cursor.close()
        print(f"{inserted_count} rows inserted successfully.")
    except Error as e:
        print(f"Error inserting data: {e}")
    except FileNotFoundError:
        print(f"CSV file '{filename}' not found.")
