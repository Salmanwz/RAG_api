import os
import logging
from fastapi import FastAPI
import chromadb
import ollama

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

MODEL_NAME = os.getenv("MODEL_NAME", "tinyllama")
logging.info(f"Using model: {MODEL_NAME}")


app = FastAPI()    # Initialize FastAPI app
chroma = chromadb.PersistentClient(path="./db")  # Initialize ChromaDB client 
collection = chroma.get_or_create_collection("docs") # Get or create collection

@app.get('/health')
def health_check():
    """Health check endpoint to verify the service is running.

    Returns:
        dict: A simple status message.
    """
    return {"status": "ok"}

@app.post("/query") 
def query(q: str):
    """Creates an endpoint to handle queries.

    Args:
        q (str): User query string.

    Returns:
        json: Generated answer from the model.
    """
    results = collection.query(query_texts=[q], n_results=1)
    context = results["documents"][0][0] if results["documents"] else ""
    logging.info(f"/query asked: {q}")
    answer = ollama.generate(
        model=MODEL_NAME,
        prompt=f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer clearly and concisely:"
    )
    
    return {answer["response"]}

@app.post("/add")
def add_knowledge(text: str):
    """ Add Context to Knowledge Base

    Args:
        text (str): Text content to be added to the knowledge base.

    Returns:
        _type_: Response indicating success or failure.
    """
    try:
        # Generate a unique ID for this document
        import uuid
        doc_id = str(uuid.uuid4())
        
        # Add the text to Chroma collection
        collection.add(documents=[text], ids=[doc_id])
        logging.info(f"/add received new text {doc_id} generated)")
        
        return {
            "status": "success",
            "message": "Content added to knowledge base",
            "id": doc_id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

