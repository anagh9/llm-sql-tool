# LLM SQL Query Tool

Convert natural language questions into SQL queries using AI.

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Database**: MySQL + Redis Cache
- **AI**: OpenAI GPT-4

## Installation

### Prerequisites

- Python 3.8+
- Node.js 18+
- MySQL running
- Redis running
- OpenAI API key

### Backend Setup

```bash
cd backend
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r query_engine/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (OpenAI key, DB credentials, Redis settings)

# Run backend
python main.py
```

Backend runs on: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your API URL (NEXT_PUBLIC_API_URL=http://localhost:8000)

# Run development server
npm run dev
```

Frontend runs on: `http://localhost:3000`

## Project Structure

```
llm_sql/
├── backend/
│   ├── main.py              (FastAPI server)
│   ├── requirements.txt
│   ├── .env.example
│   └── query_engine/        (SQL query generator)
│
├── frontend/
│   ├── app/                 (Next.js pages)
│   ├── components/          (React components)
│   ├── lib/api.ts          (API client)
│   ├── package.json
│   └── .env.local.example
│
└── assets/
```

## Quick Start

1. **Terminal 1** - Start Backend:
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```

2. **Terminal 2** - Start Frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Browser** - Open: `http://localhost:3000`

## Configuration Files

- `backend/.env.example` - Backend configuration template
- `frontend/.env.local.example` - Frontend configuration template

Copy these files and fill in your credentials:
- OpenAI API key
- MySQL connection details
- Redis connection details
- API URL (frontend only)

---

## ⚡ Quick Start (5 Minutes)

### 1️⃣ Backend Setup (Terminal 1)

```bash
cd backend

# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r query_engine/requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
python main.py
```

**Backend ready at:** `http://localhost:8000`  
**API docs at:** `http://localhost:8000/docs`

### 2️⃣ Frontend Setup (Terminal 2)

```bash
cd frontend

# Install dependencies
npm install

# Configure
cp .env.local.example .env.local
# Update NEXT_PUBLIC_API_URL if needed (default: http://localhost:8000)

# Run
npm run dev
```

**Frontend ready at:** `http://localhost:3000`

### 3️⃣ Start Using!

Open your browser to: **`http://localhost:3000`**

---

## 🔄 Architecture Overview

```
Browser (Next.js)                    http://localhost:3000
    ↓ HTTP + JSON
    ↓ TypeScript API client
    ↓
FastAPI Backend                      http://localhost:8000
    ├─ REST API Endpoints
    ├─ Session Management
    └─ Query Routing
    ↓
Query Engine (Python + MCP)
    ├─ OpenAI GPT-4 Integration
    ├─ MySQL Database Access
    └─ Redis Caching
```

---

## ✨ Key Features

✅ **Natural Language to SQL**
- Convert English questions to optimized SQL queries
- Uses OpenAI GPT-4 for intelligent query generation

✅ **Intelligent Caching**
- Redis-based caching for repeated queries
- Template management for common questions
- Fast retrieval of frequently asked questions

✅ **Modern UI**
- Beautiful, responsive chat interface
- Built with Next.js + TypeScript + Tailwind CSS
- Mobile-friendly design
- Dark mode ready (extensible)

✅ **Type-Safe Development**
- Full TypeScript support frontend & backend
- API response types
- Component prop types
- Better IDE support

✅ **Session Management**
- Conversation history per session
- Multiple independent sessions
- Clear history option

✅ **Statistics & Analytics**
- View query statistics
- Track cached queries
- Monitor usage patterns

---

## 📚 API Endpoints

### Health
- `GET /health` - Server health check

### Chat
- `POST /api/chat` - Send query
  ```
  ?message=How many users?&session_id=default
  ```

### History
- `GET /api/history` - Get conversation history
- `POST /api/clear-history` - Clear history

### Statistics
- `GET /api/stats` - Get usage statistics
- `GET /api/suggestions` - Get query suggestions
- `GET /api/templates` - Get cached queries

---

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **MCP (Model Context Protocol)** - LLM integration
- **OpenAI** - GPT-4 API
- **MySQL** - Database
- **Redis** - Caching
- **Python 3.8+**

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Icons** - Icon library
- **Axios** - HTTP client
- **Node.js 18+**

---

## 🔐 Environment Configuration

### Backend (.env)
```env
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

OPENAI_API_KEY=sk-...
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=database
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📖 Documentation

- **[backend/README.md](backend/README.md)** - Backend API setup & details
- **[frontend/README.md](frontend/README.md)** - Frontend setup & customization
- **[backend/query_engine/README.md](backend/query_engine/README.md)** - Query engine details

---

## 🚀 Development Commands

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r query_engine/requirements.txt
python main.py              # Start server
```

### Frontend
```bash
cd frontend
npm install
npm run dev               # Development
npm run build            # Production build
npm run start            # Production server
npm run type-check       # TypeScript check
```

---

## 🐳 Docker Deployment

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt query_engine/requirements.txt ./
RUN pip install -r requirements.txt -r query_engine/requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Frontend Dockerfile
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 🆘 Troubleshooting

### Backend
**Error: "Connection refused" (MySQL/Redis)**
```bash
# Check services running
mysql -u root -p -e "SELECT 1"
redis-cli ping
```

**Error: "Module not found"**
```bash
pip install -r requirements.txt -r query_engine/requirements.txt
```

### Frontend
**Error: "Cannot find module"**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Error: API calls failing**
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify backend is running
- Check browser console for CORS errors

---

## 🚢 Production Deployment

### Backend (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Frontend (Vercel)
```bash
vercel deploy
```

### Environment for Production
```env
# Backend
API_PORT=8000
DEBUG=False
OPENAI_API_KEY=sk-prod-...

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## 📊 Performance Options

- Enable Redis caching (recommended)
- Use production ASGI server (Gunicorn/Gunicorn-gevent)
- Enable Next.js output caching
- Use CDN for static files
- Database connection pooling

---

## 🤝 Contributing

Contributions welcome! Please:
1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

---

## 📝 License

See [LICENSE](LICENSE) file

---

## 🎉 Ready to Get Started?

1. **Backend:** `cd backend && python main.py`
2. **Frontend:** `cd frontend && npm run dev`
3. **Browser:** `http://localhost:3000`

**Enjoy natural language querying!** 🚀

---

## 🎯 Overview

This project bridges the gap between natural language and SQL by leveraging Large Language Models (LLM) to automatically understand user questions and generate optimized database queries. The system includes intelligent caching, template management, and token cost tracking.

### Key Features

- **Natural Language Processing**: Convert plain English questions into SQL queries
- **Intelligent Table Selection**: LLM automatically identifies relevant tables needed to answer questions
- **Smart Caching**: Redis-based caching with TTL to avoid redundant queries and API calls
- **Template System**: Store and reuse common queries and their answers
- **Cost Tracking**: Monitor OpenAI API usage and estimated costs
- **Error Handling**: Robust error management for database and API failures
- **MCP Server**: Built on Model Context Protocol for seamless integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          User Question (Natural Language)       │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  Template/Cache Check       │
        │ (Redis + templates.json)    │
        └─────────────────┬───────────┘
                          │
         ┌────────────────┴────────────────┐
         │ Cache Hit?                      │
         │ (Return Cached Answer)          │
         │ Cache Miss ↓                    │
         │                                │
         ▼                                │
    ┌────────────────────────┐           │
    │ Get Relevant Tables    │           │
    │ (LLM: GPT-4o)          │           │
    └────────────┬───────────┘           │
                 │                       │
                 ▼                       │
    ┌────────────────────────┐           │
    │ Fetch Table Schema     │           │
    │ (MySQL Database)       │           │
    └────────────┬───────────┘           │
                 │                       │
                 ▼                       │
    ┌────────────────────────┐           │
    │ Generate SQL Query     │           │
    │ (LLM: GPT-4o)          │           │
    └────────────┬───────────┘           │
                 │                       │
                 ▼                       │
    ┌────────────────────────┐           │
    │ Execute SQL Query      │────────────┐
    │ (MySQL Database)       │           │
    └────────────┬───────────┘           │
                 │                       │
                 ▼                       ▼
    ┌────────────────────────────────────────┐
    │ Format Answer & Cache Result           │
    │ (Store in Redis + templates.json)      │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │ Return Answer to User  │
    └────────────────────────┘
```

## 🌐 Full System Architecture (With Web Interface)

```
┌────────────────────────────────────────────────────────────────┐
│                      User Browser                              │
│                  (Web Chat Interface)                           │
│        http://localhost:5000 - Beautiful UI Interface           │
└────────────────────┬───────────────────────────────────────────┘
                     │ HTTP Requests
                     │ (JSON over HTTP)
                     ▼
        ┌─────────────────────────────┐
        │   Flask Web Client          │
        │      (client.py)            │
        │                             │
        │  - REST API Endpoints       │
        │  - Session Management       │
        │  - Message Routing          │
        │  - Error Handling           │
        └────────────┬────────────────┘
                     │
                     │ MCP Protocol / Function Calls
                     │
                     ▼
        ┌─────────────────────────────────────────────┐
        │     MCP Server (Main Query Processor)        │
        │          (main.py or main.py)              │
        │                                              │
        │  - Natural Language Understanding            │
        │  - Table Selection (LLM)                     │
        │  - SQL Generation (LLM)                      │
        │  - Query Execution                           │
        │  - Result Caching                            │
        └────────┬──────────────────┬─────────────────┘
                 │                  │
        ┌────────▼──────┐    ┌──────▼──────────┐
        │   MySQL DB    │    │   Redis Cache   │
        │               │    │                 │
        │ - Execute     │    │ - Store Results │
        │   Queries     │    │ - TTL Cache     │
        │ - Schema Ops  │    │ - Fast Lookups  │
        └───────────────┘    └────────┬────────┘
                                      │
                             ┌────────▼─────────┐
                             │ templates.json    │
                             │                   │
                             │ - Query Templates │
                             │ - Preset Answers  │
                             │ - Usage Stats     │
                             └───────────────────┘

        ┌────────────────────────────────────────┐
        │  OpenAI GPT-4o (External LLM)          │
        │                                         │
        │  - Table Selection                      │
        │  - SQL Generation                       │
        │  - Answer Formatting                    │
        └────────────────────────────────────────┘
```

## 📸 Interface Preview

The web interface includes:
- **Chat Interface**: Beautiful message-based UI
- **Dark Mode**: Toggle between light and dark themes
- **Real-time Updates**: Instant message display
- **Query History**: See all recent queries
- **Statistics**: Monitor usage and cache hits
- **Templates**: Quick suggestions for common queries

*Add your screenshot to `static/image.png` for visual documentation*

```
llm_sql/
├── main.py                  # Primary MCP server with core functionality
├── main.py               # Alternative version with enhanced structure
├── client.py               # Flask web interface client
├── database.py             # MySQL database operations
├── cache.py                # Redis caching utility
├── templates.json          # Cached queries and answers storage
├── requirements.txt        # Python dependencies
├── README.md              # Main documentation
├── WEBINTERFACE.md        # Web interface guide
├── static/                # Frontend assets
│   ├── style.css          # CSS styling
│   ├── script.js          # JavaScript frontend
│   └── image.png          # Interface screenshot (add your image here)
└── templates/             # HTML templates
    └── index.html         # Chat interface HTML
```

### File Descriptions

- **[main.py](main.py)**: FastMCP server that orchestrates the entire workflow
  - `ask_product_data()`: Main tool for processing natural language questions
  - `get_relevant_tables()`: Identifies necessary tables using LLM
  - `get_sql_from_llm()`: Generates SQL from natural language
  - Template management for caching

- **[main.py](main.py)**: Enhanced version (recommended for production)
  - Better error handling
  - Improved token usage tracking
  - Extended template system with usage analytics
  - More robust logging

- **[database.py](database.py)**: MySQL integration layer
  - `get_table_list()`: Retrieves all table names
  - `get_specific_schema()`: Gets schema for targeted tables (token-efficient)
  - `execute_read_query()`: Executes SELECT queries safely
  - Connection pooling and error handling

- **[cache.py](cache.py)**: Redis caching layer
  - `get_cached_query()`: Retrieves cached results
  - `set_cached_query()`: Stores query results with TTL
  - Environment-based configuration

- **[templates.json](templates.json)**: Template storage
  - Pre-computed query-answer pairs
  - Stores raw database results
  - LLM-generated answers
  - Token usage information

- **[client.py](client.py)**: Flask web client
  - RESTful API endpoints for chat
  - Session management
  - Query caching and statistics
  - Error handling and logging

- **[WEBINTERFACE.md](WEBINTERFACE.md)**: Web interface documentation
  - Setup and running instructions
  - Feature overview
  - Usage guide and examples
  - Keyboard shortcuts
  - Troubleshooting

- **[static/](static/)**: Frontend assets
  - `style.css`: Professional CSS with dark mode
  - `script.js`: Interactive JavaScript with WebSocket support
  - `image.png`: Interface screenshot/diagram

- **[templates/](templates/)**: HTML templates
  - `index.html`: Main chat interface

## 🔧 Setup & Installation

### Prerequisites

- Python 3.8+
- MySQL Server running
- Redis Server running
- OpenAI API key

### Step 1: Clone & Navigate

```bash
cd /home/anaghk/Public/Code/llm_sql
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here

# MySQL Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=your_database_name

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL=3600

# MCP Server Configuration
MCP_HOST=localhost
MCP_PORT=8000
```

### Step 5: Verify Connections

```bash
# Test MySQL connection
python3 database.py

# Test Redis connection
python3 cache.py

# Test OpenAI API
python3 -c "from openai import AsyncOpenAI; print('OpenAI SDK loaded')"
```

## 🚀 Running the Application

### ⚡ Quick Start - Run Both Server & Web Client

The easiest way to get started is to run both the MCP server and web client together.

#### **Option A: Using Two Terminal Windows (Recommended)**

**Terminal 1 - Start the MCP Server:**
```bash
cd /home/anaghk/Public/Code/llm_sql
source venv/bin/activate
python3 main.py
```

**Terminal 2 - Start the Web Client (in a new terminal):**
```bash
cd /home/anaghk/Public/Code/llm_sql
source venv/bin/activate
python3 client.py
```

**Then open in browser:** [http://localhost:5000](http://localhost:5000)

#### **Option B: Using a Bash Script (Automated)**

Create `run_all.sh` in the project root:

```bash
#!/bin/bash
echo "Starting LLM SQL Chat System..."
echo "================================"

# Activate virtual environment
source venv/bin/activate

# Start MCP Server in background
echo "[1/2] Starting MCP Server (main.py)..."
python3 main.py &
MCP_PID=$!
echo "     PID: $MCP_PID"

# Wait for MCP server to start
sleep 2

# Start Web Client in background
echo "[2/2] Starting Web Client (client.py)..."
python3 client.py &
WEB_PID=$!
echo "     PID: $WEB_PID"

echo ""
echo "✅ Both services started!"
echo "   - MCP Server:  Running (PID: $MCP_PID)"
echo "   - Web Client:  http://localhost:5000 (PID: $WEB_PID)"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Keep script running
wait
```

Make it executable and run:
```bash
chmod +x run_all.sh
./run_all.sh
```

---

### MCP Server Only (CLI Mode)

**Option 1: Using main.py (Standard)**

```bash
source venv/bin/activate
python3 main.py
```

The MCP server will start and listen for connections.

**Option 2: Using main.py (Recommended - Enhanced Version)**

```bash
source venv/bin/activate
python3 main.py
```

Features better error handling and cost tracking.

**Option 3: Run with Environment Reload**

```bash
source venv/bin/activate
python3 main.py --reload
```

---

### Web Client Only

If the MCP server is already running elsewhere:

```bash
source venv/bin/activate
python3 client.py --host 0.0.0.0 --port 5000 --debug
```

Forwarding to a remote MCP server:

```bash
source venv/bin/activate
python3 client.py --host 0.0.0.0 --port 5000
```

---

### ✅ Quick Startup Checklist

Before running both services, verify:

- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file configured with all credentials
- [ ] MySQL server running
- [ ] Redis server running
- [ ] Ports 5000 (Flask) and any MCP ports are available

### 🔧 Starting Services - Expected Output

**Terminal 1 - MCP Server:**
```
WARNING:asyncio:... Creating LLM task...
Starting main server...
Server running...
```

**Terminal 2 - Web Client:**
```
[INFO] Using main (enhanced MCP server)
 * Running on http://localhost:5000
 * Press CTRL+C to quit
```

Once both are running, open: **http://localhost:5000**

---

## 💡 Usage Examples

Once the server is running, you can ask questions:

### Example 1: Count Total Users
```
Question: "How many users are there?"
Response: (Cached) There are a total of 158 users.
```

### Example 2: Complex Aggregation
```
Question: "From order table find top 5 products which was ordered most"
Response: Top products by order quantity with detailed breakdown
```

### Example 3: Recent Products
```
Question: "From product table find 5 products who are very recent and give product_id and title"
Response: 5 most recently added products with IDs and titles
```

## 📊 How It Works

### 1. Query Caching Strategy

The system uses a **two-tier caching approach**:

| Cache Tier | Storage | TTL | Use Case |
|-----------|---------|-----|----------|
| **L1 Cache** | templates.json | Permanent | Common/preset queries |
| **L2 Cache** | Redis | 1 hour (default) | Recently executed queries |

### 2. Token Optimization

- **Selective Schema Loading**: Only fetches schemas for identified tables (not all tables)
- **Template Reuse**: Avoids re-processing identical questions
- **Cost Tracking**: Logs token usage per query for optimization

### 3. LLM Integration Flow

1. **Table Selection**: LLM identifies relevant tables from the schema
2. **Schema Fetch**: Only retrieve schemas for selected tables
3. **Query Generation**: LLM creates optimal SQL
4. **Result Processing**: Format and cache results

## 🔌 API Endpoints

### Main Tool: `ask_product_data`

**Input:**
- `question` (string): Natural language question about product data

**Output:**
- String: Formatted answer with query results

**Example:**
```python
result = await ask_product_data("How many orders are there?")
```

## 🛠️ Configuration Options

### Database Configuration
```env
DB_HOST=localhost          # MySQL server hostname
DB_USER=root              # MySQL username
DB_PASSWORD=your_pwd      # MySQL password
DB_NAME=database_name     # Database to query
```

### Cache Configuration
```env
REDIS_HOST=localhost      # Redis server hostname
REDIS_PORT=6379          # Redis port
CACHE_TTL=3600           # Cache time-to-live in seconds
```

### API Configuration
```env
OPENAI_API_KEY=sk-...    # Your OpenAI API key
OPENAI_MODEL=gpt-4o      # Model to use (default: gpt-4o)
```

## 📈 Performance Considerations

### Caching Impact
- **First query**: ~3-5 seconds (LLM processing + DB execution)
- **Cached query**: ~50-100ms (Redis lookup)
- **Template query**: <10ms (JSON lookup)

### Token Usage
- Average simple query: 500-800 tokens
- Complex aggregation: 1000-1500 tokens
- Cost per query: ~$0.005-$0.01 (with GPT-4o)

### Optimization Tips
1. Use Redis with adequate memory
2. Regularly archive old templates
3. Monitor token usage via cost tracking in main.py
4. Index frequently queried columns in MySQL

## 🐛 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Database connection failed" | MySQL not running | Start MySQL: `sudo service mysql start` |
| "No cached result" first query | Cache empty | Normal - LLM will process |
| "Error connecting to Redis" | Redis not running | Start Redis: `redis-server` |
| "Invalid API key" | Wrong OpenAI key | Check `.env` file and OpenAI dashboard |
| "Table not found" (SQL error) | Wrong table name | Verify table exists in schema |
| "MCP server not initialized" (Web Client) | MCP server not running | Start MCP: `python3 main.py` in another terminal |
| "Cannot connect to Flask" (http://localhost:5000 fails) | Web client not running | Start client: `python3 client.py` |
| "Port already in use" | Another service using port 5000 | Use different port: `python3 client.py --port 8080` or kill process: `lsof -i :5000` |
| "Module import error" in client.py | Missing dependencies | Run: `pip install -r requirements.txt` |

## 📝 Environment Template

Create `.env.example` for team reference:

```env
# Copy this file to .env and fill in your values
OPENAI_API_KEY=sk-your-key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=your_database
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL=3600
```

## � Adding Interface Screenshots

To add visual documentation of the web interface:

![LLM SQL Web Interface](assets/image.png)

## 📦 Dependencies

- **mcp**: Model Context Protocol SDK
- **mysql-connector-python**: MySQL database driver
- **redis**: Redis client library
- **python-dotenv**: Environment variable management
- **openai**: OpenAI API client (async support)
- **Flask**: Web framework
- **Flask-CORS**: CORS support for Flask

See [requirements.txt](requirements.txt) for all versions.

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use environment variables** for all credentials
3. **Validate user queries** - Sanitize inputs
4. **Restrict database user** - Use least privilege
5. **Enable Redis authentication** in production
6. **Use HTTPS** for API calls

## 📚 Additional Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [MySQL Connector Python](https://dev.mysql.com/doc/connector-python/en/)
- [Redis Documentation](https://redis.io/documentation)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Permissions:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

Conditions:
- 📋 License and copyright notice required

## 👥 Contributing

Guidelines for contributors:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📧 Support

For issues or questions:
- Check the troubleshooting section
- Review existing templates in `templates.json`
- Test database connectivity
- Verify OpenAI API credits

---

## 💬 Chat Examples & Prompts

Here are examples of queries you can ask in the chat interface. The system will automatically detect if a visualization is needed and display charts where appropriate.

### 📊 Analytics & Visualizations (With Charts)

These queries will automatically generate charts for data visualization:

#### 1. **Monthly Order Trends** (Line Chart)
```
Show me orders every month for the last year
```
**Response**: Line chart showing order count by month + text analysis
- **Chart Type**: Line Chart
- **Use Case**: Track trends over time, identify seasonal patterns
- **Visualization**: True, chart_type: "line"

#### 2. **Order Distribution by Category** (Pie Chart)
```
Show order distribution by category
```
**Response**: Pie chart breaking down orders by product category
- **Chart Type**: Pie Chart
- **Use Case**: Understand composition, see category breakdown
- **Visualization**: True, chart_type: "pie"

#### 3. **Top Products Performance** (Bar Chart)
```
Show me the top 5 products ordered most
```
**Response**: Bar chart comparing product sales
- **Chart Type**: Bar Chart
- **Use Case**: Identify best-selling products, benchmark performance
- **Visualization**: True, chart_type: "bar"

#### 4. **Revenue Analysis** (Line Chart)
```
Plot total revenue per month with trends
```
**Response**: Line chart showing revenue progression
- **Chart Type**: Line Chart
- **Use Case**: Monitor revenue performance, forecast trends
- **Visualization**: True, chart_type: "line"

#### 5. **Sales by Product Category** (Pie Chart)
```
Break down sales percentage by product type
```
**Response**: Pie chart with percentage distribution
- **Chart Type**: Pie Chart
- **Use Case**: Understand market share, optimize inventory
- **Visualization**: True, chart_type: "pie"

#### 6. **Weekly Sales Comparison** (Bar Chart)
```
Compare sales for each week this month
```
**Response**: Bar chart with weekly performance
- **Chart Type**: Bar Chart
- **Use Case**: Weekly performance tracking, consistency analysis
- **Visualization**: True, chart_type: "bar"

---

### 📈 Statistics & Metrics (Text Responses)

These queries return textual analysis without charts:

#### 1. **Total Order Count**
```
How many orders are there in total?
```
**Response**: "There are 15,847 total orders in the system..."

#### 2. **User Statistics**
```
How many users are registered?
```
**Response**: "You have 2,341 registered users..."

#### 3. **Average Order Value**
```
What is the average order value?
```
**Response**: "The average order value is $125.43..."

#### 4. **Order Status Summary**
```
How many orders are in processing status?
```
**Response**: "There are 342 orders currently in processing status..."

#### 5. **Product Performance**
```
Which product has been ordered the most?
```
**Response**: "Product 'USB-C Cable' has been ordered 1,247 times..."

#### 6. **Revenue Metrics**
```
What is the total revenue from all orders?
```
**Response**: "Total revenue is $1,987,654.32..."

#### 7. **Customer Analysis**
```
How many orders does the average customer place?
```
**Response**: "The average customer places 6.7 orders..."

#### 8. **Refund Analysis**
```
Calculate the total refunded amount from refunds
```
**Response**: "Total refunded amount is $87,932.45..."

---

### 🔍 Detailed Queries

#### 1. **Find Specific Products**
```
Find 5 most recent products with product_id and title
```
**Response**: List of 5 recent products with details

#### 2. **Customer Orders**
```
List orders from customer with ID 123
```
**Response**: Complete order history for that customer

#### 3. **Date Range Analysis**
```
How many orders were placed in March?
```
**Response**: Order count for March with breakdown

#### 4. **Price Analysis**
```
Find products priced between $50 and $100
```
**Response**: List of products in that price range with count

#### 5. **Status Breakdown**
```
Count orders by status
```
**Response**: Breakdown of orders across all statuses

---

### 🎯 Real Business Use Cases

#### Sales Queries
```
"What was our best selling month?"
"Compare last month's sales to this month"
"Show me revenue trend for the last quarter"
"Which customers spent the most?"
```

#### Inventory & Product Queries
```
"List our top 10 best sellers"
"Show products with low stock"
"Which products have never been ordered?"
"Compare sales performance by product category"
```

#### Customer Queries
```
"How many new customers this month?"
"What is customer retention rate?"
"Find customers who haven't ordered in 90 days"
"List VIP customers (high spending)"
```

#### Performance Analytics
```
"What is the average order processing time?"
"Show order completion rate by status"
"Compare Q1 vs Q2 performance"
"Analyze refund rate trends"
```

---

### 💡 Tips for Best Results

1. **Be Specific**: "Top 5 products" works better than "products"
2. **Use Time References**: "last month", "this quarter", "past 30 days"
3. **Request Visualizations**: Say "show me a chart of..." for automatic visualization
4. **Include Metrics**: "revenue", "orders", "sales", "customers"
5. **Natural Language**: Write as you would speak to a colleague

---

### 🔄 Example API Responses

#### **Response with Visualization**
```json
{
  "success": true,
  "message": "Show me orders every month",
  "answer": "Based on database analysis, order volume shows steady growth with seasonal peaks in Q4...",
  "cached": false,
  "timestamp": "2026-04-02T12:30:00.000000",
  "source": "llm",
  "visualise": true,
  "chart_type": "line",
  "chart_data": {
    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "datasets": [{
      "label": "Orders",
      "data": [1250, 1340, 1180, 1450, 1620, 1890],
      "borderColor": "rgb(75, 192, 192)",
      "backgroundColor": "rgba(75, 192, 192, 0.1)"
    }]
  }
}
```

#### **Response without Visualization**
```json
{
  "success": true,
  "message": "How many orders are there?",
  "answer": "There are 15,847 total orders in the system. Of these, 12,450 are completed, 2,150 are pending, and 1,247 are cancelled.",
  "cached": false,
  "timestamp": "2026-04-02T12:32:00.000000",
  "source": "llm",
  "visualise": false
}
```

---

### 🚀 Start Asking Questions!

1. Open [http://localhost:3000](http://localhost:3000)
2. Type any question about your database
3. Sit back and watch AI-powered answers with charts appear instantly!

**Example First Question:**
```
Show me orders every month for the last year
```

---

**Last Updated**: April 2, 2026  
**Version**: 1.1  
**Status**: Production Ready with Visualization Support
