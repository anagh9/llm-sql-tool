"""
Flask Client for LLM SQL Chat Interface
Provides a web-based chat interface to interact with the MCP server
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Import MCP modules
mcp_module = None
try:
    # Try importing main_c first (enhanced version), then main as fallback
    try:
        import main as mcp_module
        print("[INFO] Using main_c (enhanced MCP server)")
    except ImportError:
        import main as mcp_module
        print("[INFO] Using main (standard MCP server)")
except ImportError as e:
    print(f"[WARNING] Could not import MCP server module: {e}")
    print("[INFO] Proceeding with client - ensure MCP server is running separately")
    print("[INFO] Start MCP server with: python3 main_c.py (in another terminal)")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.getenv(
    'FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False
CORS(app)

# Global conversation history store (in production, use database)
conversation_history = {}
query_cache = {}


def async_route(f):
    """Decorator to handle async functions in Flask routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return decorated_function


# ==================== API Routes ====================

@app.route('/')
def index():
    """Render the chat interface"""
    return render_template('index.html', version='1.0')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'LLM SQL Chat Interface',
        'version': '1.0'
    }), 200


@app.route('/api/chat', methods=['POST'])
@async_route
async def chat():
    """
    Main chat endpoint - processes user questions and returns answers

    Request JSON:
    {
        "message": "user question",
        "session_id": "optional-session-id"
    }
    """
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing message field'
            }), 400

        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')

        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400

        logger.info(f"Processing query: {user_message}")

        # Check cache first
        cache_key = user_message.lower()
        if cache_key in query_cache:
            logger.info(f"Returning cached answer for: {user_message}")
            return jsonify({
                'success': True,
                'message': user_message,
                'answer': query_cache[cache_key]['answer'],
                'cached': True,
                'timestamp': datetime.now().isoformat(),
                'source': 'cache'
            }), 200

        # Process through MCP
        try:
            # Check if MCP module is available
            if mcp_module is None:
                return jsonify({
                    'success': False,
                    'error': 'MCP server not initialized. Please start the MCP server first: python3 main_c.py',
                    'timestamp': datetime.now().isoformat()
                }), 503

            # Use main_c's ask_product_data function
            answer = await mcp_module.ask_product_data(user_message)

            # Cache the result
            query_cache[cache_key] = {
                'question': user_message,
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            }

            # Store in conversation history
            if session_id not in conversation_history:
                conversation_history[session_id] = []

            conversation_history[session_id].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
            conversation_history[session_id].append({
                'role': 'assistant',
                'content': answer,
                'timestamp': datetime.now().isoformat()
            })

            logger.info(f"Successfully processed query")

            return jsonify({
                'success': True,
                'message': user_message,
                'answer': answer,
                'cached': False,
                'timestamp': datetime.now().isoformat(),
                'source': 'llm'
            }), 200

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error processing query: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history for a session"""
    session_id = request.args.get('session_id', 'default')
    history = conversation_history.get(session_id, [])

    return jsonify({
        'success': True,
        'session_id': session_id,
        'history': history,
        'count': len(history)
    }), 200


@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    session_id = request.get_json().get('session_id', 'default')

    if session_id in conversation_history:
        del conversation_history[session_id]
        return jsonify({
            'success': True,
            'message': f'History cleared for session: {session_id}'
        }), 200

    return jsonify({
        'success': True,
        'message': f'No history found for session: {session_id}'
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about queries"""
    total_queries = sum(len(h) for h in conversation_history.values())
    total_cached = len(query_cache)

    return jsonify({
        'success': True,
        'total_conversations': len(conversation_history),
        'total_queries': total_queries,
        'total_cached_queries': total_cached,
        'cache_queries': list(query_cache.keys())[:10]  # Last 10
    }), 200


@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get query suggestions based on templates"""
    suggestions = [
        "How many users are there?",
        "How many orders are there in processing status?",
        "Calculate the total refunded amount from refunds",
        "Find top 5 products ordered most",
        "Find 5 most recent products with product_id and title"
    ]

    return jsonify({
        'success': True,
        'suggestions': suggestions
    }), 200


@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get cached templates"""
    templates = list(query_cache.keys())

    return jsonify({
        'success': True,
        'templates': templates,
        'count': len(templates)
    }), 200


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ==================== CLI & Main ====================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='LLM SQL Chat Interface')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to bind to')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('--reload', action='store_true',
                        help='Enable auto-reload')

    args = parser.parse_args()

    logger.info(f"Starting LLM SQL Chat Interface on {args.host}:{args.port}")

    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        use_reloader=args.reload,
        threaded=True
    )
