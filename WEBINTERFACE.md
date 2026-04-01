# LLM SQL Chat Interface - Quick Start Guide

## 🚀 Running the Web Interface

### Prerequisites

Ensure you have completed the main setup from [README.md](README.md):
- ✅ Virtual environment activated
- ✅ Dependencies installed: `pip install -r requirements.txt`
- ✅ `.env` file configured with:
  - MySQL credentials
  - Redis configuration
  - OpenAI API key

### Step 1: Start the MCP Server (Terminal 1)

The MCP server needs to be running in the background:

```bash
cd /home/anaghk/Public/Code/llm_sql
source venv/bin/activate
python3 main_c.py
```

Keep this terminal running. You should see output indicating the MCP server is running.

### Step 2: Start the Flask Web Client (Terminal 2)

In a new terminal:

```bash
cd /home/anaghk/Public/Code/llm_sql
source venv/bin/activate
python3 client.py
```

**Options:**
```bash
# Standard run
python3 client.py

# Run on custom host/port
python3 client.py --host localhost --port 8080

# Debug mode (auto-reload on file changes)
python3 client.py --debug

# Debug with reload
python3 client.py --debug --reload
```

### Step 3: Open in Browser

Navigate to: **http://localhost:5000**

You should see the chat interface with the welcome message.

## 🎯 Interface Overview

### Sidebar (Left Panel)
- **Logo & Status**: Shows application name and status
- **Quick Actions**:
  - 🆕 **New Chat**: Clear all messages and start fresh
  - 🗑️ **Clear History**: Remove conversation history
  - 📊 **Statistics**: View query stats
- **Recent Queries**: Your last queries appear here
- **Quick Templates**: Pre-made query suggestions

### Chat Area (Center Panel)
- **Header**: Shows connection status and info
- **Messages**: Display conversations with timestamps
- **Input Box**: Type your questions
- **Keyboard Hints**: Shows shortcuts

### Message Display
- **User messages**: Blue bubbles (right-aligned)
- **Assistant messages**: Gray bubbles (left-aligned)
- **Cached badge**: Yellow "Cached" badge if result was retrieved from cache
- **Timestamps**: Each message shows when it was sent

## 💬 Usage Examples

### Example 1: Simple Count Query
```
User: "How many users are there?"
Assistant: "There are a total of 158 users."
```

### Example 2: Complex Aggregation
```
User: "Find top 5 products ordered most"
Assistant: [Displays structured data with products and quantities]
```

### Example 3: Using Quick Template
- Click any suggestion in the "Quick Templates" section
- Message appears in input box
- Press Enter to send

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift+Enter` | New line in input |
| `Ctrl+K` / `Cmd+K` | Focus input box |
| `Ctrl+L` / `Cmd+L` | Clear chat |
| `Esc` | Close modals |

## 🌙 Dark Mode

1. Click ⚙️ **Settings** in top-right
2. Toggle **Dark Mode** checkbox
3. Your preference is saved

## 📊 Statistics

Click 📊 **Statistics** button to see:
- Total conversations
- Total queries executed
- Cached queries count
- Recent queries list

## 💾 Caching

Two types of caching:
1. **Templates** (templates.json): Permanent storage
2. **Redis Cache**: Session-based with TTL

### Cached Results
- Show **"Cached"** badge
- Appear instantly (no LLM processing)
- Still logged in statistics

## 🔧 Configuration

Edit `.env` file to customize:

```env
# Flask Server
# FLASK_SECRET_KEY=your-secret-key

# Cache TTL (seconds)
CACHE_TTL=3600

# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=database_name

# OpenAI
OPENAI_API_KEY=sk-your-key
```

## 🐛 Troubleshooting

### "Cannot connect to MCP server"
- Ensure MCP server is running in another terminal
- Check port isn't blocked
- Verify `.env` configuration

### "Database connection failed"
```bash
# Verify MySQL is running
mysql --version
sudo service mysql status

# Test connection
python3 database.py
```

### "No suggestions appearing"
- Wait a moment for suggestions to load
- Check browser console for errors (F12)
- Verify API is responding

### "Slow responses"
- Check network latency
- Verify OpenAI API isn't rate-limited
- Clear cache if it's very large
- Restart Redis: `redis-cli FLUSHALL`

### Port Already in Use
```bash
# Find process on port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port
python3 client.py --port 8080
```

## 🧪 Testing with Selenium

The interface is Selenium-friendly with proper element IDs:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("http://localhost:5000")

# Send a message
input_field = driver.find_element(By.ID, "messageInput")
input_field.send_keys("How many users are there?")

# Click send
send_button = driver.find_element(By.ID, "sendBtn")
send_button.click()

# Wait for response
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "message"))
)
```

## 📱 Mobile Support

The interface is fully responsive:
- Works on tablets
- Optimized for mobile browsers
- Sidebar collapses on small screens
- Touch-friendly buttons

## 🚫 Stopping the Server

### Flask Web Server
Press `Ctrl+C` in the Flask terminal

### MCP Server
Press `Ctrl+C` in the MCP terminal

### Clean Shutdown
```bash
# Kill both processes
pkill -f "python3 client.py"
pkill -f "python3 main_c.py"
```

## 📈 Performance Tips

1. **Use Redis**: Ensure Redis is running for caching
2. **Query Templates**: Reuse common queries
3. **Monitor Logs**: Check console for errors
4. **Clear Old Cache**: Periodically clean templates.json
5. **Database Indexes**: Optimize frequently queried tables

## 🔐 Security in Production

Before deploying:

1. Set `FLASK_SECRET_KEY` in `.env`
2. Enable HTTPS (use reverse proxy like Nginx)
3. Implement authentication
4. Use environment-based configuration
5. Set `debug=False` in production
6. Use strong database passwords
7. Restrict API access

## 📚 API Endpoints

All endpoints return JSON:

```
GET  /                    # Main chat page
GET  /api/health          # Health check
POST /api/chat            # Send message
GET  /api/history         # Get conversation history
POST /api/clear-history   # Clear history for session
GET  /api/stats           # Get statistics
GET  /api/suggestions     # Get query suggestions
GET  /api/templates       # Get cached templates
```

## 📞 Support

- Check [README.md](README.md) for project documentation
- Review [templates.json](templates.json) for example queries
- Check browser console (F12) for JavaScript errors
- Verify network requests in DevTools

---

**Version**: 1.0  
**Last Updated**: April 1, 2026  
**Status**: Production Ready
