"""
Database operations using SQLite3 models
Handles both user database queries (from business DB) and history tracking
"""

import mysql.connector
import os
from decimal import Decimal
from datetime import date, time, datetime as dt
from dotenv import load_dotenv
from typing import Optional
import time as time_module

# Import SQLite models
from models import User, ChatSession, ChatHistory, initialize_database

# Load variables from .env file
load_dotenv()


# ==================== Initialize SQLite on module load ====================

# Initialize SQLite database on import
try:
    initialize_database()
    print("✓ SQLite database initialized")
except Exception as e:
    print(f"Warning: Could not initialize SQLite database: {e}")


# ==================== Decimal/Date Conversion Utilities ====================

def convert_to_serializable(obj):
    """
    Recursively convert MySQL result objects (Decimal, date, time, datetime) 
    to JSON-serializable types (float, string, etc)
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (date, time, dt)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    return obj


# ==================== MySQL Connection (for user database queries) ====================

def get_mysql_connection():
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


def get_table_list():
    """Returns a simple list of all table names from MySQL."""
    conn = get_mysql_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        return tables
    except Exception as e:
        print(f"Error getting table list: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_specific_schema(tables):
    """Gets schema only for specific tables to save tokens."""
    if not tables:
        return "No tables identified."

    conn = get_mysql_connection()
    if not conn:
        return "Database connection failed."

    cursor = conn.cursor()
    try:
        schema_info = ""
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            col_desc = ", ".join([f"{c[0]} ({c[1]})" for c in columns])
            schema_info += f"Table: {table} | Columns: {col_desc}\n"
        return schema_info
    except Exception as e:
        return f"Error getting schema: {str(e)}"
    finally:
        cursor.close()
        conn.close()


async def execute_query(query):
    """Execute a SELECT query on the MySQL database."""
    conn = get_mysql_connection()
    if not conn:
        return f"Error: Database connection failed"

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return convert_to_serializable(result)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def execute_read_query(query: str):
    """Executes a SELECT query and returns the results."""
    connection = get_mysql_connection()
    if connection is None:
        return "Database connection failed."

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            return "No data found."

        result = convert_to_serializable(result)
        return result
    except Exception as err:
        return f"SQL Error: {err}"
    finally:
        cursor.close()
        connection.close()


# ==================== SQLite History Functions ====================

def get_or_create_user_from_session(session_id: str, username: Optional[str] = None):
    """
    Get or create a user for a session.
    If username not provided, uses 'unknown' user.
    """
    try:
        if username:
            user = User.get_by_username(username)
            if not user:
                user_id = User.create(username, user_type='registered')
                return user_id
            return user['id']
        else:
            # Get or create unknown user
            return User.get_or_create_unknown_user()
    except Exception as e:
        print(f"Error getting/creating user: {e}")
        return User.get_or_create_unknown_user()


def get_or_create_chat_session(session_id: str, username: Optional[str] = None):
    """
    Get or create a chat session.
    Returns database ID of the session.
    """
    try:
        # Check if session exists
        existing = ChatSession.get_by_session_id(session_id)
        if existing:
            return existing['id']

        # Get or create user
        user_id = get_or_create_user_from_session(session_id, username)

        # Create session
        session_db_id = ChatSession.create(session_id, user_id)
        return session_db_id
    except Exception as e:
        print(f"Error managing chat session: {e}")
        raise


def save_chat_history(
    session_id: str,
    user_question: str,
    gpt_response: str,
    sql_query: Optional[str] = None,
    chart_type: Optional[str] = None,
    visualise: bool = False,
    cached: bool = False,
    source: str = 'llm',
    total_tokens: Optional[int] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    database_results: Optional[str] = None,
    sql_execution_time: Optional[float] = None,
    error_message: Optional[str] = None,
    execution_status: str = 'success',
    metadata: Optional[dict] = None
) -> bool:
    """
    Save a complete chat history entry with all details.
    """
    try:
        # Get session database ID
        session_obj = ChatSession.get_by_session_id(session_id)
        if not session_obj:
            print(f"Session {session_id} not found")
            return False

        session_db_id = session_obj['id']
        user_id = session_obj['user_id']

        # Save to history
        ChatHistory.create(
            session_id=session_db_id,
            user_id=user_id,
            user_question=user_question,
            gpt_response=gpt_response,
            sql_query=sql_query,
            chart_type=chart_type,
            visualise=visualise,
            cached=cached,
            source=source,
            total_tokens=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=model,
            temperature=temperature,
            top_p=top_p,
            database_results=database_results,
            sql_execution_time=sql_execution_time,
            error_message=error_message,
            execution_status=execution_status,
            metadata=metadata
        )

        # Update session stats
        ChatSession.update_stats(
            session_id,
            increment_total=True,
            increment_cached=cached,
            increment_visualized=visualise
        )

        print(f"✓ Chat history saved for session {session_id}")
        return True
    except Exception as e:
        print(f"Error saving chat history: {e}")
        return False


def get_session_history(session_id: str, limit: int = 50):
    """
    Get chat history for a session.
    """
    try:
        session = ChatSession.get_by_session_id(session_id)
        if not session:
            return []

        history = ChatHistory.get_session_history(session['id'], limit)
        return history
    except Exception as e:
        print(f"Error getting session history: {e}")
        return []


def get_user_history(username: str, limit: int = 100):
    """
    Get chat history for a user across all sessions.
    """
    try:
        user = User.get_by_username(username)
        if not user:
            return []

        history = ChatHistory.get_user_history(user['id'], limit)
        return history
    except Exception as e:
        print(f"Error getting user history: {e}")
        return []


def search_history(query: str, limit: int = 50):
    """
    Search chat history by question or response.
    """
    try:
        return ChatHistory.search_history(query, limit)
    except Exception as e:
        print(f"Error searching history: {e}")
        return []


def get_history_stats():
    """
    Get comprehensive history statistics.
    """
    try:
        return ChatHistory.get_statistics()
    except Exception as e:
        print(f"Error getting history stats: {e}")
        return {}


def delete_user_history(username: str) -> bool:
    """
    Delete all history for a user.
    """
    try:
        user = User.get_by_username(username)
        if not user:
            return False

        # This would require implementing in models
        print(f"Note: Full user deletion not yet implemented")
        return True
    except Exception as e:
        print(f"Error deleting user history: {e}")
        return False


# Keep compatibility with old function names
def save_query_history(session_id: str, question: str, answer: str,
                       sql_query: str = None, chart_type: str = None,
                       visualise: bool = False, cached: bool = False):
    """
    Compatibility wrapper for old save_query_history function.
    """
    return save_chat_history(
        session_id=session_id,
        user_question=question,
        gpt_response=answer,
        sql_query=sql_query,
        chart_type=chart_type,
        visualise=visualise,
        cached=cached
    )


def initialize_history_table():
    """
    Compatibility function - database is auto-initialized.
    """
    return True


# Optional: Legacy MySQL history functions (if still needed)
def get_all_history(limit: int = 100):
    """Get all chat history."""
    try:
        return ChatHistory.get_all_history(limit)
    except Exception as e:
        print(f"Error getting all history: {e}")
        return []
