import os
import uuid
import logging
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from endee import Endee, Precision
from endee.schema import VectorItem
from google import genai

# Monkey-patch VectorItem for endee SDK bug
def _vector_item_get(self, key, default=None):
    return getattr(self, key, default)
VectorItem.get = _vector_item_get

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Endee Semantic Search API")

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- MODEL --------------------
model_name = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
logger.info(f"Loading model: {model_name}")
model = SentenceTransformer(model_name)

# -------------------- ENDEE --------------------
ENDEE_URL = os.getenv("ENDEE_URL", "http://localhost:8080/api/v1")

client = Endee()
client.set_base_url(ENDEE_URL)

INDEX_NAME = "documents_index"
DIMENSION = 384

# 🔥 FINAL TUNED SETTINGS
SIMILARITY_THRESHOLD = 0.2
TOP_K_DEFAULT = 5
MAX_RESULTS = 2
MAX_CONTEXT_CHUNKS = 2

# -------------------- STARTUP --------------------
@app.on_event("startup")
async def startup_event():
    try:
        logger.info(f"Connecting to Endee at {ENDEE_URL}")
        try:
            client.create_index(
                name=INDEX_NAME,
                dimension=DIMENSION,
                space_type="cosine",
                precision=Precision.FLOAT16
            )
            logger.info("Index ready")
        except Exception as e:
            logger.info(f"Index exists or skipped: {e}")
    except Exception as e:
        logger.error(f"Endee connection failed: {e}")

# -------------------- MODELS --------------------
class SearchQuery(BaseModel):
    query: str
    top_k: int = TOP_K_DEFAULT

class TextDocumentIngest(BaseModel):
    text: str
    title: str

# -------------------- CHUNKING --------------------
def chunk_text(text: str, chunk_size=150, overlap=30) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

# -------------------- INGEST --------------------
@app.post("/api/ingest/text")
async def ingest_text(doc: TextDocumentIngest):
    if not doc.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
        

    chunks = chunk_text(doc.text)
    print(f"Inserting {len(chunks)} chunks")   # ✅ correct place

    try:
        index = client.get_index(name=INDEX_NAME)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    vectors = []

    for chunk in chunks:
        vector = model.encode(chunk).tolist()

        vectors.append({
            "id": str(uuid.uuid4()),
            "vector": vector,
            "meta": {
                "title": doc.title,
                "text_chunk": chunk
            }
        })

    try:
        index.upsert(vectors)
        print("Inserted successfully") 
        return {
            "status": "success",
            "chunks_inserted": len(vectors)
        }
        
    except Exception as e:
        logger.error(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------- GEMINI --------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "dummy_key_to_prevent_startup_crash")
try:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Gemini Client: {e}")
    genai_client = None

# -------------------- SEARCH --------------------
@app.post("/api/search")
async def semantic_search(query: SearchQuery):

    if not query.query.strip():
        return {"results": [], "answer": "Please enter a valid query."}

    try:
        index = client.get_index(name=INDEX_NAME)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    query_vector = model.encode(query.query).tolist()

    try:
        raw_results = index.query(
            vector=query_vector,
            top_k=query.top_k
        )

        filtered_results = []
        context_chunks = []

        print("\n--- DEBUG RESULTS ---")

        for res in raw_results:
            if isinstance(res, dict):
                similarity = res.get("similarity", 0) 
                meta = res.get("meta", {})
                res_id = res.get("id")
            else:
                similarity = getattr(res, "similarity", 0) or getattr(res, "Similarity", 0)
                meta = getattr(res, "meta", {}) or getattr(res, "Meta", {})
                res_id = getattr(res, "id", None) or getattr(res, "ID", None)

            print(f"TRUE SIM: {similarity} | TEXT: {meta.get('text_chunk', '')[:50]}")

            # 🔥 HARD FILTER
            if similarity is None or similarity < SIMILARITY_THRESHOLD:
                continue

            filtered_results.append({
                "id": res_id,
                "similarity": round(similarity, 3),
                "meta": meta
            })

            if "text_chunk" in meta:
                context_chunks.append(meta["text_chunk"])

        # Limit results strictly
        filtered_results = filtered_results[:MAX_RESULTS]
        context_chunks = context_chunks[:MAX_CONTEXT_CHUNKS]

        if not context_chunks:
            return {
                "results": [],
                "answer": "No relevant information found."
            }

        # -------------------- RAG --------------------
        context_text = "\n\n---\n\n".join(context_chunks)

        prompt = f"""
You are a helpful AI assistant.

Use ONLY the provided context to answer the question.
If the answer is not in the context, say:
"I don't have enough information in my knowledge base."

Context:
{context_text}

Question:
{query.query}
"""
        print("\n--- DEBUG PROMPT ---\n" + prompt)

        try:
            response = genai_client.models.generate_content(
                model="gemma-3-1b-it",
                contents=prompt
            )
            answer = response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            if "429" in str(e) or "quota" in str(e).lower():
                answer = "Rate limit exceeded (15 requests/minute). Please wait a few seconds and try again."
            else:
                answer = "AI response generation failed."

        return {
            "results": filtered_results,
            "answer": answer
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------- HEALTH --------------------
@app.get("/api/health")
def health():
    return {"status": "ok"}

# -------------------- FRONTEND --------------------
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

# -------------------- RUN --------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)