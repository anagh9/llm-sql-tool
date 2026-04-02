import os
import json
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP
from openai import AsyncOpenAI

import database
import cache

load_dotenv()

# MCP Server
mcp = FastMCP("ProductQueryTool")
TEMPLATES_FILE = "templates.json"

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ==================== Decimal Conversion Utilities ====================

def convert_decimals(obj):
    """
    Recursively convert Decimal objects to float for JSON serialization
    Handles nested dicts, lists, and mixed structures from database queries
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_decimals(item) for item in obj]
    return obj


# ==================== Utility Functions ====================

def load_templates():
    if not os.path.exists(TEMPLATES_FILE):
        return {}

    try:
        with open(TEMPLATES_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_template(question, sql, raw_data, answer, usage):
    data = load_templates()

    # Convert Decimal objects to float for JSON serialization
    raw_data_converted = convert_decimals(raw_data)
    usage_converted = convert_decimals(usage)

    data[question.lower()] = {
        "question": question,
        "query": sql,
        "raw_data": raw_data_converted,
        "answer": answer,
        "usage": usage_converted
    }

    with open(TEMPLATES_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_template(question):
    data = load_templates()
    return data.get(question.lower())


def calculate_cost(usage):
    """
    Approx cost calculation (adjust pricing as per OpenAI pricing)
    """
    cost_per_1k_tokens = 0.005  # example pricing
    return round((usage["total_tokens"] / 1000) * cost_per_1k_tokens, 6)


# -----------------------------
# LLM Functions
# -----------------------------

async def get_relevant_tables(question):
    all_tables = database.get_table_list()

    prompt = f"""
    Given these tables: {all_tables}
    Which tables are required to answer this question?

    Question: {question}

    Return ONLY a comma-separated list of table names.
    """

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    selected = response.choices[0].message.content.strip().split(",")

    return (
        [s.strip() for s in selected if s.strip() in all_tables],
        response.usage
    )


async def generate_sql(question, schema):
    prompt = f"""
    You are a MySQL expert.

    Schema:
    {schema}

    Convert the question into a valid MySQL query.

    Question: {question}

    Return ONLY SQL.
    """

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Return only raw SQL"},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql, response.usage


async def generate_final_answer(question, raw_results):
    prompt = f"""
    Question: {question}
    Data: {raw_results}

    Convert this into a clean, human-readable answer.
    """

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip(), response.usage


async def generate_short_answer_for_visualization(question, raw_results):
    """
    Generate a concise answer for visualization/plot requests.
    Returns just the key datapoints without lengthy analysis.
    """
    prompt = f"""
    Question: {question}
    Data: {raw_results}

    Provide a VERY SHORT answer (1-2 sentences) with just the key datapoints.
    No lengthy explanation or analysis - just the essential numbers and insights.
    Format: Use concise bullet points or short sentences with numbers.
    
    Example format:
    - January: $1,500
    - February: $2,000
    - March: $1,800
    """

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip(), response.usage


def is_visualization_request(question: str) -> bool:
    """
    Detect if question is requesting a visualization/plot/graph
    """
    viz_keywords = [
        'plot', 'graph', 'chart', 'visualize', 'visualization',
        'trend', 'monthly', 'weekly', 'daily', 'timeline',
        'per month', 'per week', 'per day', 'show by',
        'breakdown', 'distribution', 'analytics'
    ]
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in viz_keywords)


def format_chart_data(raw_results: list, chart_type: str = "line") -> dict:
    """
    Convert raw query results into chart.js compatible format.
    Handles various data structures and converts them to proper chart format.

    Returns:
        {
            "labels": [...],
            "datasets": [{
                "label": "...",
                "data": [...],
                "borderColor": "...",
                "backgroundColor": "..."
            }]
        }
    """
    if not raw_results or not isinstance(raw_results, list):
        return {"labels": [], "datasets": []}

    # Determine if this is a single value or multiple data points
    first_row = raw_results[0] if raw_results else {}

    if not isinstance(first_row, dict):
        return {"labels": [], "datasets": []}

    keys = list(first_row.keys())

    # Handle different data structures
    if len(keys) == 1:
        # Single column - treat as values with index as labels
        key = keys[0]
        values = [row[key] for row in raw_results]
        labels = [f"Item {i+1}" for i in range(len(values))]

        return {
            "labels": labels,
            "datasets": [{
                "label": key,
                "data": values,
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.1)"
            }]
        }

    elif len(keys) == 2:
        # Two columns - first is label, second is value
        label_key = keys[0]
        value_key = keys[1]

        labels = [str(row[label_key]) for row in raw_results]
        values = [float(row[value_key]) if isinstance(row[value_key], (int, float, Decimal)) else 0
                  for row in raw_results]

        # Choose colors based on chart type
        if chart_type == "pie":
            colors = [
                "rgba(255, 99, 132, 0.8)",
                "rgba(54, 162, 235, 0.8)",
                "rgba(255, 206, 86, 0.8)",
                "rgba(75, 192, 192, 0.8)",
                "rgba(153, 102, 255, 0.8)",
                "rgba(255, 159, 64, 0.8)",
            ]
            bg_colors = [colors[i % len(colors)] for i in range(len(values))]

            return {
                "labels": labels,
                "datasets": [{
                    "label": value_key,
                    "data": values,
                    "backgroundColor": bg_colors
                }]
            }
        else:  # line or bar
            return {
                "labels": labels,
                "datasets": [{
                    "label": value_key,
                    "data": values,
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.1)"
                }]
            }

    else:
        # Multiple columns - use first as labels, others as datasets
        label_key = keys[0]
        labels = [str(row[label_key]) for row in raw_results]

        datasets = []
        for i, key in enumerate(keys[1:]):
            values = [float(row[key]) if isinstance(row[key], (int, float, Decimal)) else 0
                      for row in raw_results]

            colors = [
                {"border": "rgb(75, 192, 192)",
                 "bg": "rgba(75, 192, 192, 0.1)"},
                {"border": "rgb(201, 103, 146)",
                 "bg": "rgba(201, 103, 146, 0.1)"},
                {"border": "rgb(255, 159, 64)",
                 "bg": "rgba(255, 159, 64, 0.1)"},
            ]
            color = colors[i % len(colors)]

            datasets.append({
                "label": key,
                "data": values,
                "borderColor": color["border"],
                "backgroundColor": color["bg"]
            })

        return {
            "labels": labels,
            "datasets": datasets
        }


# Store raw results globally for chart data extraction
_last_raw_results = None


def store_raw_results(results):
    """Store raw results for chart data extraction"""
    global _last_raw_results
    _last_raw_results = results


def get_last_raw_results():
    """Get stored raw results"""
    global _last_raw_results
    return _last_raw_results


@mcp.tool()
async def ask_product_data(question: str) -> str:
    """
    Main intelligent query handler using LLM.
    """

    # 1. Check template cache
    cached_entry = get_template(question)
    if cached_entry:
        usage = cached_entry.get("usage", {})
        return f"(Cached | Tokens: {usage.get('total_tokens', 0)}) {cached_entry['answer']}"

    # 2. Get relevant tables
    relevant_tables, table_usage = await get_relevant_tables(question)
    schema = database.get_specific_schema(relevant_tables)

    # 3. Generate SQL
    sql_query, sql_usage = await generate_sql(question, schema)

    # 4. Execute query
    raw_results = await database.execute_query(sql_query)

    # 5. Convert Decimal objects to float for JSON serialization
    raw_results_converted = convert_decimals(raw_results)

    # Store raw results for chart data extraction (if visualization request)
    if is_visualization_request(question):
        store_raw_results(raw_results_converted)

    # 6. Generate final answer - use short format for visualizations
    if is_visualization_request(question):
        final_answer, final_usage = await generate_short_answer_for_visualization(question, raw_results_converted)
    else:
        final_answer, final_usage = await generate_final_answer(question, raw_results_converted)

    # 7. Combine usage
    total_usage = {
        "prompt_tokens": (
            table_usage.prompt_tokens +
            sql_usage.prompt_tokens +
            final_usage.prompt_tokens
        ),
        "completion_tokens": (
            table_usage.completion_tokens +
            sql_usage.completion_tokens +
            final_usage.completion_tokens
        ),
        "total_tokens": (
            table_usage.total_tokens +
            sql_usage.total_tokens +
            final_usage.total_tokens
        ),
        "models": ["gpt-4o", "gpt-4o-mini"],
        "timestamp": datetime.utcnow().isoformat()
    }

    total_usage["estimated_cost"] = calculate_cost(total_usage)

    # 8. Save template (with converted data)
    save_template(
        question=question,
        sql=sql_query,
        raw_data=raw_results_converted,
        answer=final_answer,
        usage=total_usage
    )

    return final_answer


@mcp.tool()
def query_product_data(question: str) -> str:
    """
    Simple fallback query (non-LLM)
    """

    # 1. Redis cache
    cached_res = cache.get_cached_query(question)
    if cached_res:
        return f"(Cached) {cached_res}"

    # 2. Basic logic
    if "how many users" in question.lower():
        sql = "SELECT COUNT(*) as count FROM users"
    else:
        return "Currently supports only user count queries."

    # 3. Execute
    result = database.execute_read_query(sql)
    count = result[0].get("count", "No count found")

    # 4. Cache result
    cache.set_cached_query(question, count)

    return str(count)


# -----------------------------
# Run Server
# -----------------------------

if __name__ == "__main__":
    mcp.run()
