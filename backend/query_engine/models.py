"""
SQLite Models for User, Chat Session, and Chat History Tracking
Designed for comprehensive query and response logging
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

# Database path
DB_PATH = os.getenv('SQLITE_DB_PATH', os.path.join(
    os.path.dirname(__file__), '../data/app.db'))

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db_connection():
    """Get SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


# ==================== Database Initialization ====================

def initialize_database():
    """Initialize all database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            user_type TEXT DEFAULT 'anonymous',  -- 'registered' or 'anonymous'
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            metadata TEXT
        )
        """)

        # Chat Sessions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            total_queries INTEGER DEFAULT 0,
            total_cached_queries INTEGER DEFAULT 0,
            total_visualized_queries INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # Chat History Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            user_question TEXT NOT NULL,
            gpt_response TEXT NOT NULL,
            sql_query TEXT,
            sql_execution_time REAL,
            database_results LONGTEXT,
            chart_type TEXT,
            visualise BOOLEAN DEFAULT FALSE,
            cached BOOLEAN DEFAULT FALSE,
            source TEXT DEFAULT 'llm',
            total_tokens INTEGER,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            model TEXT,
            temperature REAL,
            top_p REAL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            query_hash TEXT,
            error_message TEXT,
            execution_status TEXT DEFAULT 'success',
            metadata TEXT,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # Create indexes for better query performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON chat_sessions(user_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON chat_sessions(session_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_session_id ON chat_history(session_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_user_id ON chat_history(user_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_generated_at ON chat_history(generated_at)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_visualise ON chat_history(visualise)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_cached ON chat_history(cached)")

        conn.commit()
        print("✓ Database tables initialized successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        return False
    finally:
        conn.close()


# ==================== User Model ====================

class User:
    """User model for tracking registered and anonymous users."""

    @staticmethod
    def get_or_create_unknown_user() -> int:
        """Get or create the 'unknown' user for anonymous sessions."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Try to get existing unknown user
            cursor.execute("SELECT id FROM users WHERE username = 'unknown'")
            result = cursor.fetchone()

            if result:
                return result['id']

            # Create unknown user
            cursor.execute("""
            INSERT INTO users (username, user_type, first_name, last_name, is_active)
            VALUES ('unknown', 'anonymous', 'Unknown', 'User', TRUE)
            """)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error managing unknown user: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def create(username: str, email: Optional[str] = None, first_name: Optional[str] = None,
               last_name: Optional[str] = None, user_type: str = 'registered', metadata: Optional[Dict] = None) -> int:
        """Create a new user."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            metadata_str = json.dumps(metadata) if metadata else None
            cursor.execute("""
            INSERT INTO users (username, email, user_type, first_name, last_name, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, user_type, first_name, last_name, metadata_str))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"User {username} already exists")
            raise
        except sqlite3.Error as e:
            print(f"Error creating user: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username: str) -> Optional[Dict]:
        """Get user by username."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            conn.close()


# ==================== Chat Session Model ====================

class ChatSession:
    """Chat session model for tracking user sessions."""

    @staticmethod
    def create(session_id: str, user_id: int, metadata: Optional[Dict] = None) -> int:
        """Create a new chat session."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            metadata_str = json.dumps(metadata) if metadata else None
            cursor.execute("""
            INSERT INTO chat_sessions (session_id, user_id, metadata)
            VALUES (?, ?, ?)
            """, (session_id, user_id, metadata_str))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating session: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_by_session_id(session_id: str) -> Optional[Dict]:
        """Get session by session_id."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM chat_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error getting session: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(session_db_id: int) -> Optional[Dict]:
        """Get session by database ID."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM chat_sessions WHERE id = ?", (session_db_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error getting session: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update_stats(session_id: str, increment_total: bool = False,
                     increment_cached: bool = False, increment_visualized: bool = False) -> bool:
        """Update session statistics."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Build update query dynamically
            updates = []
            if increment_total:
                updates.append("total_queries = total_queries + 1")
            if increment_cached:
                updates.append(
                    "total_cached_queries = total_cached_queries + 1")
            if increment_visualized:
                updates.append(
                    "total_visualized_queries = total_visualized_queries + 1")

            if updates:
                update_str = ", ".join(updates)
                cursor.execute(f"""
                UPDATE chat_sessions
                SET {update_str}
                WHERE session_id = ?
                """, (session_id,))
                conn.commit()

            return True
        except sqlite3.Error as e:
            print(f"Error updating session stats: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def end_session(session_id: str) -> bool:
        """Mark session as ended."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
            UPDATE chat_sessions
            SET ended_at = CURRENT_TIMESTAMP, is_active = FALSE
            WHERE session_id = ?
            """, (session_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error ending session: {e}")
            return False
        finally:
            conn.close()


# ==================== Chat History Model ====================

class ChatHistory:
    """Chat history model for tracking all queries and responses."""

    @staticmethod
    def create(
        session_id: int,
        user_id: int,
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
        metadata: Optional[Dict] = None
    ) -> int:
        """Create a new chat history entry with comprehensive details."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Convert complex types to JSON strings
            database_results_str = json.dumps(
                database_results) if database_results else None
            metadata_str = json.dumps(metadata) if metadata else None

            cursor.execute("""
            INSERT INTO chat_history (
                session_id, user_id, user_question, gpt_response, sql_query,
                chart_type, visualise, cached, source, total_tokens,
                prompt_tokens, completion_tokens, model, temperature, top_p,
                database_results, sql_execution_time, error_message,
                execution_status, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, user_id, user_question, gpt_response, sql_query,
                chart_type, visualise, cached, source, total_tokens,
                prompt_tokens, completion_tokens, model, temperature, top_p,
                database_results_str, sql_execution_time, error_message,
                execution_status, metadata_str
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating chat history: {e}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_session_history(session_db_id: int, limit: int = 50) -> List[Dict]:
        """Get chat history for a session."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT * FROM chat_history
            WHERE session_id = ?
            ORDER BY generated_at DESC
            LIMIT ?
            """, (session_db_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting session history: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_user_history(user_id: int, limit: int = 100) -> List[Dict]:
        """Get chat history for a user across all sessions."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT * FROM chat_history
            WHERE user_id = ?
            ORDER BY generated_at DESC
            LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting user history: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_all_history(limit: int = 500) -> List[Dict]:
        """Get all chat history."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT * FROM chat_history
            ORDER BY generated_at DESC
            LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting all history: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """Get comprehensive statistics."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            stats = {}

            # Total queries
            cursor.execute("SELECT COUNT(*) as count FROM chat_history")
            stats['total_queries'] = cursor.fetchone()['count']

            # Cached queries
            cursor.execute(
                "SELECT COUNT(*) as count FROM chat_history WHERE cached = TRUE")
            stats['cached_queries'] = cursor.fetchone()['count']

            # Visualized queries
            cursor.execute(
                "SELECT COUNT(*) as count FROM chat_history WHERE visualise = TRUE")
            stats['visualized_queries'] = cursor.fetchone()['count']

            # By chart type
            cursor.execute("""
            SELECT chart_type, COUNT(*) as count
            FROM chat_history
            WHERE visualise = TRUE
            GROUP BY chart_type
            """)
            stats['by_chart_type'] = {row['chart_type']
                : row['count'] for row in cursor.fetchall()}

            # Unique users
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) as count FROM chat_history")
            stats['unique_users'] = cursor.fetchone()['count']

            # Unique sessions
            cursor.execute(
                "SELECT COUNT(DISTINCT session_id) as count FROM chat_history")
            stats['unique_sessions'] = cursor.fetchone()['count']

            # Total tokens used
            cursor.execute(
                "SELECT SUM(total_tokens) as total FROM chat_history WHERE total_tokens IS NOT NULL")
            result = cursor.fetchone()
            stats['total_tokens'] = result['total'] or 0

            # Average response time
            cursor.execute(
                "SELECT AVG(sql_execution_time) as avg FROM chat_history WHERE sql_execution_time IS NOT NULL")
            result = cursor.fetchone()
            stats['avg_sql_execution_time'] = result['avg'] or 0

            return stats
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return {}
        finally:
            conn.close()

    @staticmethod
    def search_history(query: str, limit: int = 50) -> List[Dict]:
        """Search chat history by question or response."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            search_pattern = f"%{query}%"
            cursor.execute("""
            SELECT * FROM chat_history
            WHERE user_question LIKE ? OR gpt_response LIKE ?
            ORDER BY generated_at DESC
            LIMIT ?
            """, (search_pattern, search_pattern, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error searching history: {e}")
            return []
        finally:
            conn.close()
