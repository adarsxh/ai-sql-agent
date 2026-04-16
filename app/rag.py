from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np
import faiss
import numpy as np
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("openai_api_key"))


schema_texts = []
index = None

def build_index(schema_list):
    global schema_texts, index
    
    schema_texts = schema_list
    embeddings = []

    for text in schema_list:
        emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        ).data[0].embedding
        
        embeddings.append(emb)

    embeddings = np.array(embeddings).astype("float32")
    os.makedirs("embeddings", exist_ok=True)
    np.save("embeddings/schema_embeddings.npy", embeddings)

    with open("embeddings/schema_texts.json", "w") as f:
        json.dump(schema_list, f)
    
    faiss.normalize_L2(embeddings)
    
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    print("Schema embeddings indexed successfully for the first time and saved.")
    

def load_or_build(schema_list):
    global index, schema_texts

    if os.path.exists("embeddings/schema_embeddings.npy"):
        print("Loading embeddings from disk...")

        embeddings = np.load("embeddings/schema_embeddings.npy")
        
        with open("embeddings/schema_texts.json", "r") as f:
            schema_texts = json.load(f)

    else:
        print("Building embeddings...")
        return build_index(schema_list)

    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)



def retrieve_schema(query, k=5):
    query_vec = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    query_vec = np.array([query_vec]).astype("float32")
    faiss.normalize_L2(query_vec)

    distances, indices = index.search(query_vec, k)

    return [schema_texts[i] for i in indices[0]]