
import mysql.connector
from mysql.connector import Error


def get_connection():

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="smart_agriculture_db"
        )

        if connection.is_connected():
            print("MySQL connected successfully!")
            return connection

    except Error as error:
        print("Database connection failed:", error)

    return None
