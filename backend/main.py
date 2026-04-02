"""
Backend REST API for LLM SQL Query Tool
Provides API endpoints that frontend communicates with
"""

import asyncio
import os
import json
from decimal import Decimal
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

# Import query engine
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'query_engine'))

try:
    from query_engine import main as query_engine
    from query_engine import database
except ImportError:
    query_engine = None
    database = None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== JSON Serialization Utilities ====================

def convert_to_json_serializable(obj):
    """
    Recursively convert all non-JSON-serializable objects to serializable types.
    Handles: Decimal, datetime, and nested structures
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    return obj


# ==================== Custom JSON Encoder ====================

class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for FastAPI to handle Decimal and other non-serializable types
    """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# ==================== Initialize FastAPI App ====================

app = FastAPI(
    title="LLM SQL Query API",
    description="REST API for natural language to SQL query conversion",
    version="1.0.0",
    json_encoders={Decimal: float, datetime: str}
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://localhost:3001"],  # Next.js dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (use database in production)
conversation_history = {}
query_cache = {}


# ==================== Startup Event ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database tables and resources on app startup."""
    logger.info("Starting up LLM SQL Query API...")

    if database:
        logger.info("Initializing query history table...")
        database.initialize_history_table()
    else:
        logger.warning("Database module not available")


# ==================== Models ====================

class ChatRequest:
    def __init__(self, message: str, session_id: str = "default"):
        self.message = message
        self.session_id = session_id


# ==================== Helper Functions ====================

def should_visualize(message: str, answer: str) -> dict:
    """
    Determine if response should include visualization
    Returns dict with visualization config if applicable

    Visualization is recommended for:
    - Trend analysis (line charts)
    - Distribution/breakdown (pie charts)
    - Comparison/analytics (bar charts)
    """
    message_lower = message.lower()
    answer_lower = answer.lower()

    # Keywords that indicate visualization should be used
    visualization_keywords = [
        'graph', 'chart', 'plot', 'visualize', 'visualization', 'analytics', 'trend',
        'monthly', 'weekly', 'daily', 'per month', 'per week', 'per day',
        'orders', 'sales', 'revenue', 'distribution', 'breakdown', 'segment',
        'compare', 'comparison', 'analysis', 'report', 'statistics', 'summary',
        'growth', 'increase', 'decrease', 'change', 'over time', 'time series',
        'performance', 'metrics', 'data', 'volume', 'count', 'by', 'category',
        'quarter', 'year', 'annual', 'monthly average', 'top', 'bottom',
        'rank', 'list', 'show', 'display', 'view', 'percentage', 'share'
    ]

    has_viz_keyword = any(
        keyword in message_lower for keyword in visualization_keywords)

    if has_viz_keyword:
        # Pie chart detection - for distribution/breakdown/percentage
        if any(word in message_lower for word in ['pie', 'percentage', '%', 'distribution', 'breakdown', 'segment', 'share', 'portion']):
            return {"visualise": True, "chart_type": "pie", "description": "pie"}

        # Line chart detection - for time series and trends
        elif any(word in message_lower for word in ['trend', 'over time', 'monthly', 'weekly', 'daily', 'quarter', 'year', 'growth', 'forecast', 'time series', 'timeline']):
            return {"visualise": True, "chart_type": "line", "description": "trend"}

        # Default to bar chart for comparison/analytics
        else:
            return {"visualise": True, "chart_type": "bar", "description": "comparison"}

    return {"visualise": False, "chart_type": None}


def format_visualization_response(user_message: str, answer: str, viz_config: dict) -> dict:
    """
    Format response with visualization metadata
    (Actual chart data will be added by the API endpoint after extraction)
    """
    response = {
        "success": True,
        "message": user_message,
        "answer": answer,
        "cached": False,
        "timestamp": datetime.now().isoformat(),
        "source": "llm",
        "visualise": viz_config["visualise"],
    }

    if viz_config["visualise"]:
        response["chart_type"] = viz_config["chart_type"]
        # chart_data will be added by the API endpoint

    return response


# ==================== Health & Status ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "LLM SQL Query API",
        "version": "1.0.0",
        "query_engine": "ready" if query_engine else "unavailable"
    }


# ==================== Chat Endpoints ====================

@app.post("/api/chat")
async def chat(message: str, session_id: str = "default"):
    """
    Main chat endpoint - processes user questions and returns answers

    Args:
        message: User question
        session_id: Session identifier (optional)

    Returns:
        JSON response with answer, metadata, and status
    """
    try:
        if not message or not message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )

        user_message = message.strip()
        logger.info(f"Processing query: {user_message}")

        # Initialize session
        chat_session = database.get_or_create_chat_session(session_id)

        # Check cache first
        cache_key = user_message.lower()
        if cache_key in query_cache:
            logger.info(f"Returning cached answer for: {user_message}")
            cached_item = query_cache[cache_key]
            response = {
                "success": True,
                "message": user_message,
                "answer": cached_item['answer'],
                "cached": True,
                "timestamp": datetime.now().isoformat(),
                "source": "cache",
                "visualise": cached_item.get('visualise', False)
            }
            if cached_item.get('visualise'):
                response["chart_type"] = cached_item.get('chart_type')
                if cached_item.get('chart_data'):
                    response["chart_data"] = cached_item.get('chart_data')
            return convert_to_json_serializable(response)

        # Process through query engine
        if query_engine is None:
            raise HTTPException(
                status_code=503,
                detail="Query engine not initialized"
            )

        try:
            # Call query engine's main function
            start_time = datetime.utcnow()
            answer = await query_engine.ask_product_data(user_message)
            end_time = datetime.utcnow()

            # Check if response should include visualization
            viz_config = should_visualize(user_message, answer)

            # Extract chart data for visualization requests
            chart_data = None
            if viz_config["visualise"]:
                try:
                    raw_results = query_engine.get_last_raw_results()
                    if raw_results:
                        chart_data = query_engine.format_chart_data(
                            raw_results,
                            chart_type=viz_config["chart_type"]
                        )
                except Exception as chart_err:
                    logger.warning(
                        f"Could not extract chart data: {str(chart_err)}")
                    chart_data = None

            # Cache the result
            query_cache[cache_key] = {
                'question': user_message,
                'answer': answer,
                'timestamp': datetime.now().isoformat(),
                'visualise': viz_config["visualise"],
                'chart_type': viz_config["chart_type"],
                'chart_data': chart_data
            }

            # Save to database history
            if database:
                try:
                    usage = {
                        "prompt_tokens": 0,  # Replace with actual token usage
                        "completion_tokens": 0,  # Replace with actual token usage
                        "total_tokens": 0,  # Replace with actual token usage
                        "model": "gpt-4o",  # Replace with actual model name
                        "temperature": 0.7,  # Replace with actual temperature
                        "top_p": 1.0  # Replace with actual top_p
                    }

                    database.save_chat_history(
                        session_id=session_id,
                        user_question=user_message,
                        gpt_response=answer,
                        sql_query=query_engine.get_last_sql_query(),
                        chart_type=viz_config.get("chart_type"),
                        visualise=viz_config.get("visualise", False),
                        cached=False,
                        source="query_engine",
                        total_tokens=usage["total_tokens"],
                        prompt_tokens=usage["prompt_tokens"],
                        completion_tokens=usage["completion_tokens"],
                        model=usage["model"],
                        temperature=usage["temperature"],
                        top_p=usage["top_p"],
                        database_results=raw_results if raw_results else None,
                        sql_execution_time=(
                            end_time - start_time).total_seconds(),
                        error_message=None,
                        execution_status="success",
                        metadata={}
                    )
                except Exception as db_err:
                    logger.warning(
                        f"Failed to save query to history: {str(db_err)}")

            logger.info(f"Successfully processed query")

            # Return formatted response with visualization if applicable
            response = format_visualization_response(
                user_message, answer, viz_config)
            if chart_data:
                response['chart_data'] = chart_data
            return convert_to_json_serializable(response)

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as exc:
        logger.error(f"Unexpected error: {str(exc)}")
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error"
        )


# ==================== History Endpoints ====================

@app.get("/api/history")
async def get_history(session_id: str = "default"):
    """Get conversation history for a session"""
    try:
        history = conversation_history.get(session_id, [])
        return convert_to_json_serializable({
            "success": True,
            "session_id": session_id,
            "history": history,
            "count": len(history)
        })
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching history"
        )


@app.post("/api/clear-history")
async def clear_history(session_id: str = "default"):
    """Clear conversation history for a session"""
    try:
        if session_id in conversation_history:
            del conversation_history[session_id]
            return {
                "success": True,
                "message": f"History cleared for session: {session_id}"
            }

        return {
            "success": True,
            "message": f"No history found for session: {session_id}"
        }
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error clearing history"
        )


# ==================== Statistics Endpoints ====================

@app.get("/api/stats")
async def get_stats():
    """Get statistics about queries"""
    try:
        total_queries = sum(len(h) for h in conversation_history.values())
        total_cached = len(query_cache)

        return {
            "success": True,
            "total_conversations": len(conversation_history),
            "total_queries": total_queries,
            "total_cached_queries": total_cached,
            "cache_queries": list(query_cache.keys())[:10]
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching statistics"
        )


# ==================== Suggestions & Templates ====================

@app.get("/api/suggestions")
async def get_suggestions():
    """Get query suggestions"""
    try:
        suggestions = [
            "How many users are there?",
            "How many orders are in processing status?",
            "Calculate the total refunded amount from refunds",
            "Find top 5 products ordered most",
            "Find 5 most recent products with product_id and title"
        ]
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Error fetching suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching suggestions"
        )


@app.get("/api/templates")
async def get_templates():
    """Get cached templates"""
    try:
        templates = list(query_cache.keys())
        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching templates"
        )


# ==================== Visualization Endpoints ====================

@app.post("/api/visualize")
async def visualize_data(sql_query: str, chart_type: str = "line"):
    """
    Generate chart data from a SQL query result.
    Useful for creating custom visualizations from raw SQL queries.

    Args:
        sql_query: SQL query to execute
        chart_type: Type of chart ('line', 'bar', 'pie')

    Returns:
        Chart data in chart.js format
    """
    try:
        if not sql_query or not sql_query.strip():
            raise HTTPException(
                status_code=400,
                detail="SQL query cannot be empty"
            )

        if chart_type not in ['line', 'bar', 'pie']:
            raise HTTPException(
                status_code=400,
                detail="Chart type must be 'line', 'bar', or 'pie'"
            )

        logger.info(
            f"Generating visualization for query with chart type: {chart_type}")

        # Execute the query
        try:
            raw_results = await query_engine.database.execute_query(sql_query)
        except Exception as db_err:
            logger.error(f"Database query error: {str(db_err)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to execute query: {str(db_err)}"
            )

        if not raw_results:
            raise HTTPException(
                status_code=400,
                detail="Query returned no results"
            )

        # Format chart data
        try:
            chart_data = query_engine.format_chart_data(
                raw_results, chart_type=chart_type)
        except Exception as chart_err:
            logger.error(f"Chart formatting error: {str(chart_err)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to format chart data: {str(chart_err)}"
            )

        return {
            "success": True,
            "chart_type": chart_type,
            "chart_data": chart_data,
            "data_points": len(raw_results),
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in visualization: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error generating visualization"
        )


# ==================== History Endpoints ====================

@app.get("/api/history/session")
async def get_session_history_endpoint(session_id: str = "default", limit: int = 50):
    """
    Get query history for a specific session.

    Args:
        session_id: Session identifier
        limit: Maximum number of records to return (default 50)

    Returns:
        List of history records sorted by creation time (newest first)
    """
    try:
        if not database:
            raise HTTPException(
                status_code=503,
                detail="Database module not available"
            )

        history = database.get_session_history(session_id, limit)
        return {
            "success": True,
            "session_id": session_id,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Error fetching session history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching session history"
        )


@app.get("/api/history/all")
async def get_all_history_endpoint(limit: int = 100):
    """
    Get all query history across all sessions.

    Args:
        limit: Maximum number of records to return (default 100)

    Returns:
        List of all history records sorted by creation time (newest first)
    """
    try:
        if not database:
            raise HTTPException(
                status_code=503,
                detail="Database module not available"
            )

        history = database.get_all_history(limit)
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Error fetching all history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching all history"
        )


@app.get("/api/history/stats")
async def get_history_stats_endpoint():
    """
    Get statistics about query history.

    Returns:
        Dictionary with history statistics including total queries, cached queries, etc.
    """
    try:
        if not database:
            raise HTTPException(
                status_code=503,
                detail="Database module not available"
            )

        stats = database.get_history_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching history stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching history stats"
        )


@app.delete("/api/history/session")
async def delete_session_history_endpoint(session_id: str = "default"):
    """
    Delete all history for a specific session.

    Args:
        session_id: Session identifier

    Returns:
        Success status
    """
    try:
        if not database:
            raise HTTPException(
                status_code=503,
                detail="Database module not available"
            )

        success = database.delete_session_history(session_id)
        if success:
            return {
                "success": True,
                "message": f"Deleted history for session {session_id}"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete session history"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error deleting session history"
        )


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# ==================== Startup & Main ====================

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    logger.info(f"Starting LLM SQL Query API on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=debug
    )
