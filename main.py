from fastmcp import FastMCP
import database
import cache

# Create the MCP server
mcp = FastMCP("ProductQueryTool")


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
