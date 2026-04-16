from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(api_key=os.getenv("openai_api_key"))

def generate_sql(question, schema_context, additional_schema_texts):
    intent_prompt = f"""
    You are a query classifier.

    Your job is to decide whether the user query is related to the database.

    Database contains:
    - customers
    - orders
    - products
    - payments
    - reviews
    - order_items

    Rules:
    - Accept even short or incomplete queries if they refer to data (e.g., "revenue by adarsh")
    - Accept queries with names, products, cities
    - Reject only if:
        - Completely meaningless
        - Abusive or random text
        - Not related to data
    IMPORTANT:
    - NEVER assume IDs or values
    - If a name is given (like customer name), JOIN with appropriate table to find it
    - Do NOT hardcode values like 12345

    Question: {question}

    Answer only YES or NO.
    """

    response1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": intent_prompt}],
        max_tokens=150
    )
    
    intent = response1.choices[0].message.content.strip().upper()
    print(f"Intent classification: {intent}")
    if not intent.startswith("YES"):
        return {
            "error": "Invalid or irrelevant query",
            "data": []
        }

    
    prompt = f"""
    You are a SQL expert.

    Database schema:
    {schema_context}

    Additional schema information:
    {additional_schema_texts}

    
    - Use only the tables provided
    - Use correct joins if needed
    - Do not hallucinate tables or columns
    - Return only SQL without backticks.
    - use decimal notation for numbers
    - DO NOT use MySQL functions like DATE_FORMAT
    - Use DuckDB functions only:
        - DATE_TRUNC for grouping dates
        - STRFTIME for formatting
    - If unsure, prefer DATE_TRUNC
    - make sure when you match customer name or product name, watch for both upper case and lower case
    - Use ONLY column names exactly as given. Do NOT guess or shorten column names. If column is product_name, do NOT use name.
    Column Usage Rules:
    - product_id is numeric → NEVER use LOWER or string comparison
    - product_name is text → use LOWER for comparisons
    - Always match text queries with text columns
    

    Question:
    {question}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    
    return response.choices[0].message.content.strip()