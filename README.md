# AI SQL Agent

AI-powered SQL agent that converts natural language queries into executable SQL using RAG-based schema grounding.

Unlike traditional text-to-SQL systems, this approach reduces hallucinations by retrieving only the relevant schema context before query generation.

## Why This Project

Text-to-SQL systems often fail because the model does not have the right schema context at generation time. This project addresses that by using a retrieval layer before SQL generation.

Instead of sending the entire database structure every time, the application:
- extracts schema from loaded tables
- embeds schema descriptions using OpenAI embeddings
- retrieves the most relevant schema chunks with FAISS
- prompts the model with only the relevant schema context
- executes the generated SQL against DuckDB

This makes the system more grounded, more modular, and easier to extend.

## Features

- Natural language to SQL generation
- Retrieval-augmented schema grounding
- Dynamic schema extraction from DuckDB tables
- Embedding-based schema retrieval with FAISS
- SQL generation with OpenAI models
- Basic SQL safety validation before execution
- Automatic retry when generated SQL fails
- FastAPI endpoint for API access
- Dockerized setup for local containerized deployment

## Key Challenges Solved

- Prevented hallucinated joins by grounding SQL generation in retrieved schema
- Handled incorrect SQL generation using a retry mechanism with error feedback
- Reduced embedding cost by caching schema embeddings and FAISS index
- Improved query accuracy by combining dynamic schema extraction with contextual hints

## Architecture

The request flow is:
```
User Query
↓
Schema Retrieval (FAISS + Embeddings)
↓
LLM → SQL Generation
↓
Validation + Retry
↓
Execution (DuckDB)
↓
Result
```
## Tech Stack

- FastAPI
- OpenAI API
- FAISS
- DuckDB
- NumPy
- Python Dotenv
- Docker
- Uvicorn

## Project Structure

```text
.
├── app/
│   ├── main.py           # FastAPI app and orchestration
│   ├── db.py             # DuckDB loading, schema extraction, validation, execution
│   ├── rag.py            # Schema embedding, caching, FAISS retrieval
│   └── sql_generator.py  # Intent classification and SQL generation
├── data/                 # Source CSV datasets
├── embeddings/           # Cached schema embeddings and schema text
├── Dockerfile
├── requirements.txt
└── README.md

```

## Dataset

The application loads CSV files from the `data/` directory into DuckDB at startup.

Current tables:

- `customers`
- `products`
- `reviews`
- `orders`
- `payments`
- `order_items`

DuckDB is used as the local analytical database, and schemas are extracted dynamically from the loaded tables.

## API Usage

### POST `/query`

Send a natural language question and receive generated SQL with query results.

### Request

```json
{
  "question": "Show total revenue by customer"
}
```

## Response

```json
{
  "question": "Show total revenue by customer",
  "sql": "SELECT ...",
  "row_count": 5,
  "result": [
    {
      "customer_name": "Example Customer",
      "total_revenue": 1200.5
    }
  ]
}
```

---

## Local Setup

1. Install Dependencies
`pip install -r requirements.txt`

2. Add environment variables
Create a .env file in the project root:
`openai_api_key=your_openai_api_key_here`

3. Run the API
`uvicorn app.main:app --reload`

The API will be available at
`http://127.0.0.1:8000`

Interactive API docs
`http://127.0.0.1:8000/docs`

## Docker Setup

Build the Docker image:

```bash
docker build -t ai-sql-agent .
```
Run the container:
```bash
docker run -p 8000:8000 --env-file .env ai-sql-agent
```
The API will be available at:
```bash
http://localhost:8000
```
Interactive docs:
```bash
http://localhost:8000/docs
```
## Example Questions
Try asking:

- Which product did Adarsh buy?
- Show total revenue by customer
- Which products have the highest sales?
- Show all orders placed by Rahul
- What is the average rating by product?
- Which payment methods are used most often?

## How RAG Is Used
This project uses retrieval-augmented generation to improve SQL accuracy.

At startup:

CSV files are loaded into DuckDB
Table schemas are extracted
Schema descriptions are converted into embeddings
FAISS indexes the schema embeddings
Embeddings are cached in the embeddings/ directory
At query time:

The user question is embedded
FAISS retrieves relevant schema chunks
Retrieved schema context is passed to the SQL-generation prompt
The model generates DuckDB-compatible SQL
SQL is validated and executed

## Safety Layer
Before running SQL, the application performs a basic safety check and rejects unsafe operations such as:

- DROP
- DELETE
- INSERT
- UPDATE
If query execution fails, the system attempts one repair pass by sending the SQL error back to the model.

## Limitations
This project is a prototype and is not fully production-ready yet.

Current limitations:

- SQL validation is rule-based, not parser-based
- prompts are stored directly in application code
- there is no authentication or rate limiting
- cached embeddings do not automatically detect schema changes
- there are no automated tests yet
- observability and logging are minimal
- the app currently works with local CSV-backed DuckDB tables

## Future Improvements
Planned improvements:

- add parser-based SQL validation
- add unit and integration tests
- add structured logging
- support live database connections
- add schema versioning for embedding cache invalidation
- move prompts and model settings into config files
- add authentication and rate limiting
- add Docker health checks
- add CI/CD deployment workflow

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key used for embeddings and SQL generation |

## Project Status

This project is an educational prototype focused on demonstrating RAG-based text-to-SQL architecture. It is suitable for learning, experimentation, and portfolio demonstration, but requires stronger validation, testing, authentication, and observability before production use.
