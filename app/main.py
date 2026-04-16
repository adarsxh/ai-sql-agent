from fastapi import FastAPI
from pydantic import BaseModel
from app.sql_generator import generate_sql
from app.db import run_query
from app.rag import retrieve_schema
from app.db import load_data, get_schema
from app.rag import load_or_build

app = FastAPI()

# request schema
class QueryRequest(BaseModel):
    question: str

# dummy schema (replace later with dynamic)


load_data()
schema_list = get_schema()
load_or_build(schema_list)

additional_schema_texts = '''
Table: customers
Description: Stores customer profile information. Use this table to match customer names.
Primary key: customer_id

Table: orders
Description: Stores orders placed by customers.
Primary key: order_id
Foreign key: customer_id -> customers.customer_id

Table: order_items
Description: Stores products purchased in each order.
Foreign key: order_id -> orders.order_id
Foreign key: product_id -> products.product_id

Table: products
Description: Stores product details.
Primary key: product_id

Table: reviews
Description: Stores product ratings/reviews given by customers. Use this table only for review, rating, or feedback questions.
Foreign key: customer_id -> customers.customer_id
Foreign key: product_id -> products.product_id

Table: payments
Description: Stores payment information for orders.
Foreign key: order_id -> orders.order_id
'''

@app.post("/query")
def query_db(request: QueryRequest):
    schema_context = "\n\n".join(retrieve_schema(request.question))
    sql = generate_sql(request.question, schema_context, additional_schema_texts)

    if "error" in sql:
        return {
            "question": request.question,
            "sql": None,
            "row_count": 0,
            "result": [],
            "error": sql["error"]
        } 
    
    result = run_query(sql)

    if "error" in result:
        fix_prompt = f"""
        The following SQL failed:

        {sql}

        Error:
        {result["error"]}

        Fix the query using the schema.
        Return only SQL.
        """
        print(f"Error in SQL execution: {result['error']}, trying again!")
        sql = generate_sql(fix_prompt, schema_context, additional_schema_texts)
        result = run_query(sql)
        # print(result)

    return {
    "question": request.question,
    "sql": sql,
    "row_count": len(result.get('data', [])) if isinstance(result.get('data'), list) else 0,
    "result": result.get('data', [])[:10]  # limit rows
    }