import os, requests, logging, json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mitreattack.stix20 import MitreAttackData
import chromadb, ollama

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

MODEL_NAME = os.getenv("MODEL_NAME", "tinyllama")
logging.info(f"Using model: {MODEL_NAME}")

app = FastAPI(title="Security RAG API", version="1.0.0")
chroma = chromadb.PersistentClient(path="./db")
collection = chroma.get_or_create_collection("security_kb")


# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok", "docs": collection.count()}


# Endpoint to handle queries
@app.post("/ask")
def ask(q: str):
    """Query Endpoint.

    Args:
        q (str): Question text

    Returns:
        _type_: Response with answer
    """
    try:
        # Find relevant context
        results = collection.query(query_texts=[q], n_results=3)
        context = "\n\n".join(results["documents"][0] if results["documents"] else [])
        
        # Generate response with enhanced prompt
        prompt = f"""You are a cybersecurity expert assistant. Use the following context to answer the question.

                    Context:{context}

                    Question: {q}

                    Provide a clear, actionable answer. If the context mentions MITRE ATT&CK techniques, include the technique IDs. If discussing detection, mention specific tools or data sources.

        Answer:"""
            
        answer = ollama.generate(
                model=MODEL_NAME,
                prompt=prompt
            )
            
        return {
                "question": q,
                "answer": answer["response"],

            }
    
    except Exception as e:

        logging.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to load MITRE ATT&CK data
@app.post("/load-mitre")
def load_mitre():
    """ Endpoint to Load Mitre Data

    """
    # Download latest data
    url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    r = requests.get(url)
    with open("./tmp/attack.json", "wb") as f:
        f.write(r.content)
    
    # Load with MITRE library (handles all the parsing)
    data = MitreAttackData("./tmp/attack.json")
    
    docs = []
    ids = []
    
    # Just get techniques - simple!
    for tech in data.get_techniques(remove_revoked_deprecated=True):
        text = f"{tech.name} ({tech.id})\n{tech.description}"
        docs.append(text)
        ids.append(tech.id)
    
    # Embed everything at once
    collection.add(documents=docs, ids=ids)
    
    return {"loaded": len(docs)}