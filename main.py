import os
import json
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


# -----------------------------
# Utility Functions
# -----------------------------

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

    data[question.lower()] = {
        "question": question,
        "query": sql,
        "raw_data": raw_data,
        "answer": answer,
        "usage": usage
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


# -----------------------------
# MCP Tools
# -----------------------------

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

    # 5. Generate final answer
    final_answer, final_usage = await generate_final_answer(question, raw_results)

    # 6. Combine usage
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

    # 7. Save template
    save_template(
        question=question,
        sql=sql_query,
        raw_data=raw_results,
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
