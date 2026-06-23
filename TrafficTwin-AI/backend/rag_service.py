import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

from rag.retriever import RAGSystem

load_dotenv()

app = FastAPI(
    title="TrafficTwin AI RAG Service",
    description="Separate RAG microservice for incident similarity search and indexing",
    version="1.0.0"
)

rag_system = RAGSystem()
index_path = os.getenv("RAG_INDEX_PATH", "models/faiss_index.pkl")


class SearchRequest(BaseModel):
    incident: Dict
    k: Optional[int] = 5


class IndexRequest(BaseModel):
    incident: Dict
    incident_id: int


@app.on_event("startup")
def load_rag_index():
    if os.path.exists(index_path):
        try:
            rag_system.load(index_path)
            print(f"Loaded RAG index from {index_path}")
        except Exception as exc:
            raise RuntimeError(f"Failed to load RAG index: {exc}")
    else:
        print(f"RAG index not found at {index_path}. Starting with an empty index.")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "TrafficTwin AI RAG Service",
        "index_size": rag_system.get_index_size()
    }


@app.post("/search")
def search_similar(req: SearchRequest):
    try:
        similar_incidents = rag_system.retrieve_similar(req.incident, k=req.k)
        return {"similar_incidents": similar_incidents}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG search failed: {exc}")


@app.post("/index")
def index_incident(req: IndexRequest):
    try:
        rag_system.index_incident(req.incident, req.incident_id)
        rag_system.save(index_path)
        return {
            "status": "indexed",
            "incident_id": req.incident_id,
            "index_size": rag_system.get_index_size()
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG indexing failed: {exc}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)