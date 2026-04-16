import duckdb
import numpy as np
import os

con = duckdb.connect()

def load_data():
    data_path = "data"
    
    for file in os.listdir(data_path):
        if file.endswith(".csv"):
            table_name = file.replace(".csv", "")
            file_path = os.path.join(data_path, file)
            
            con.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM read_csv_auto('{file_path}')
            """)
            print(f"Loaded {table_name} from {file_path}")


def get_schema():
    tables = con.execute("SHOW TABLES").fetchall()

    schema_texts = []
    
    for (table,) in tables:
        columns = con.execute(f"DESCRIBE {table}").fetchall()
        col_text = "\n".join([f"- {col[0]} ({col[1]})" for col in columns])
        schema_text = f"""
        Table: {table}
        Columns:
        {col_text}
        """
        
        schema_texts.append(schema_text)
        print(f"Extracted schema for {table}")

    print(schema_texts)
    
    return schema_texts



def validate_sql(sql):
    sql_lower = sql.lower()

    if "drop" in sql_lower or "delete" in sql_lower:
        return False
    
    if "insert" in sql_lower or "update" in sql_lower:
        return False

    return True

def run_query(sql):
    try:
        if not validate_sql(sql):
            return {"error": "Unsafe SQL query detected."}
        result = con.execute(sql).fetchdf()
        result = result.replace({np.nan: None})
        data = result.to_dict(orient="records")
        # print(data)
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}