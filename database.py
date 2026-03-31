import mysql.connector
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None


def execute_read_query(query: str):
    """
    Executes a SELECT query and returns the results.
    We use a dictionary cursor to make the output easy for the AI to parse.
    """
    connection = get_db_connection()
    if connection is None:
        return "Database connection failed."

    print(f"Database connection established: {connection is not None}")

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query)
        result = cursor.fetchall()

        # If the result is empty, return a friendly message
        if not result:
            return "No data found."

        print(f"Query executed successfully: {result}")
        print(f"Total Number of Users: {result}")
        return result
    except mysql.connector.Error as err:
        return f"SQL Error: {err}"
    finally:
        cursor.close()
        connection.close()
