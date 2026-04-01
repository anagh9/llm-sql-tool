import os

from fastmcp import FastMCP
import database
import cache
import json
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv


load_dotenv()


# Create the MCP server
mcp = FastMCP("ProductQueryTool")
TEMPLATES_FILE = "templates.json"
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def get_relevant_tables(question):
    """Uses LLM to pick which tables are needed based on the question (Fuzzy Match)."""
    all_tables = database.get_table_list()
    prompt = f"Given these tables: {all_tables}, which ones are needed to answer: '{question}'? Return only a comma-separated list of table names."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    selected = response.choices[0].message.content.strip().split(',')
    return [s.strip() for s in selected if s.strip() in all_tables]


def get_template(question):
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r') as f:
            try:
                data = json.load(f)
                return data.get(question.lower())
            except json.JSONDecodeError:
                return None
    return None

def save_template(question, sql, raw_data, answer):
    data = {}
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r') as f:
            data = json.load(f)
    data[question.lower()] = sql


    data[question.lower()] = {
        "question": question,
        "query": sql,
        "raw_data": raw_data,
        "answer": answer
    }

    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_sql_from_llm(user_question, schema):
    prompt = f"""
    You are a MySQL expert. Given this schema: {schema}
    Convert the user question into a valid MySQL query.
    User Question: {user_question}
    Return ONLY the SQL query. No explanation.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
              "content": prompt},
            {"role": "user", "content": user_question}
        ],

        temperature=0.2,
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content.strip()


@mcp.tool()
def ask_product_data(question: str) -> str:
    """Ask any question about the product data."""

    cached_entry = get_template(question)
    if cached_entry:
        return f"(Cached) {cached_entry['answer']}"

    relevant_tables = get_relevant_tables(question)
    schema = database.get_specific_schema(relevant_tables)

    # 3. Generate SQL
    sql_prompt = f"Schema: {schema}\nQuestion: {question}\nGenerate only the MySQL query."
    sql_res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You output only raw SQL."},
                  {"role": "user", "content": sql_prompt}]
    )

    sql_query = sql_res.choices[0].message.content.strip().replace(
        '```sql', '').replace('```', '')

    # 4. Save to templates
    # save_template(question, sql_query)

    # 5. Execute
    raw_results = database.execute_query(sql_query)

    # 6. Curate Response
    curate_prompt = f"Question: {question}\nData: {raw_results}\nSummarize this nicely for a human."
    final_res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": curate_prompt}]
    )
    final_answer = final_res.choices[0].message.content.strip()
    save_template(
        question=question,
        sql=sql_query,
        raw_data=raw_results,
        answer=final_answer
    )
    return final_answer


@mcp.tool()
def query_product_data(question: str) -> str:
    """
    Analyzes a user question, checks the cache, 
    and queries the MySQL database if needed.
    """
    # 1. Check Redis Cache
    cached_res = cache.get_cached_query(question)
    if cached_res:
        return f"(Cached) {cached_res}"

    # 2. Hardcoded logic or LLM-generated SQL (Simplest version)
    if "how many users" in question.lower():
        sql = "SELECT COUNT(*) as count FROM users"
    else:
        return "I only support user count queries for now."

    # 3. Execute and Cache
    result = database.execute_read_query(sql)
    cache.set_cached_query(question, result)

    return str(result[0].get('count', 'No count found'))


if __name__ == "__main__":
    mcp.run()
    # ask_product_data("How many banners are there?")
