import json
import os
import time
import anthropic

from database import query_database

SYSTEM_PROMPT = """You are a data analyst assistant. You have access to a sales database with the following schema:

Table: sales
Columns:
- id (INTEGER, primary key)
- region (TEXT): North, South, East, West
- product_category (TEXT): Electronics, Clothing
- quarter (TEXT): Q1 2025, Q2 2025
- revenue (REAL): revenue in dollars
- units_sold (INTEGER): number of units sold

When asked a question about the data, use the query_database tool to run a SQL query and then provide a clear, concise answer based on the results. Always use SQLite-compatible SQL syntax."""

TOOLS = [
    {
        "name": "query_database",
        "description": "Execute a read-only SQL query against the sales database and return the results as a list of rows. Only SELECT statements are allowed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "A valid SQLite SELECT query to execute against the sales database.",
                }
            },
            "required": ["sql"],
        },
    }
]

BLOCKED_KEYWORDS = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]


def validate_sql(sql: str) -> str | None:
    sql_upper = sql.upper().strip()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in sql_upper:
            return f"Blocked: SQL contains disallowed keyword '{keyword}'. Only SELECT queries are permitted."
    return None

def run_agent(question: str, messages: list | None = None) -> dict:
    client = anthropic.Anthropic()

    if messages is None:
        messages = []

    messages.append({"role": "user", "content": question})

    total_input_tokens = 0
    total_output_tokens = 0
    generated_sql = None
    query_results = None
    start_time = time.time()

    while True:
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        if response.stop_reason == "tool_use":
            tool_use_block = next(
                block for block in response.content if block.type == "tool_use"
            )

            tool_name = tool_use_block.name
            tool_input = tool_use_block.input
            tool_use_id = tool_use_block.id

            messages.append({"role": "assistant", "content": response.content})

            if tool_name == "query_database":
                sql = tool_input["sql"]
                generated_sql = sql

                validation_error = validate_sql(sql)
                if validation_error:
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": validation_error,
                                    "is_error": True,
                                }
                            ],
                        }
                    )
                    return {
                        "question": question,
                        "query": sql,
                        "results": [],
                        "answer": validation_error,
                        "tokens_used": {
                            "input": total_input_tokens,
                            "output": total_output_tokens,
                        },
                        "response_time_ms": int((time.time() - start_time) * 1000),
                        "error": True,
                    }

                try:
                    query_results = query_database(sql)
                    tool_result_content = json.dumps(query_results)
                except Exception as e:
                    tool_result_content = f"Error executing query: {str(e)}"

                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": tool_result_content,
                            }
                        ],
                    }
                )
        else:
            answer = ""
            for block in response.content:
                if hasattr(block, "text"):
                    answer += block.text

            return {
                "question": question,
                "query": generated_sql,
                "results": query_results,
                "answer": answer,
                "tokens_used": {
                    "input": total_input_tokens,
                    "output": total_output_tokens,
                },
                "response_time_ms": int((time.time() - start_time) * 1000),
                "error": False,
            }

        

if __name__ == "__main__":
    from database import init_database

    init_database()
    result = run_agent("What are the total sales by region?")
    print(f"SQL: {result['query']}")
    print(f"Answer: {result['answer']}")
    print(f"Tokens: {result['tokens_used']}")