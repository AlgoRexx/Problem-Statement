import nest_asyncio
import uvicorn
import os
import shutil
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from urllib.parse import urljoin, urlparse

# Apply nest_asyncio to prevent event loop issues in Jupyter
nest_asyncio.apply()

# Define the database path
DB_PATH = "./chroma_db"

# Initialize FastAPI app
app = FastAPI()

# Load Embedding Model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(
    name="web_embeddings",
    embedding_function=SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
)

# Load T5-Small for Text Generation
generator = pipeline("text2text-generation", model="t5-small")



# Define API request models
class URLInput(BaseModel):
    url: str

class QueryInput(BaseModel):
    query: str


def is_scrapable(url: str) -> bool:
    """
    Check if a website allows web scraping by inspecting robots.txt.
    Wikipedia allows scraping, so it should be exempted.
    """
    parsed_url = urlparse(url)

    # Wikipedia allows scraping, so skip the check for Wikipedia URLs
    if "wikipedia.org" in parsed_url.netloc:
        return True  

    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

    try:
        response = requests.get(robots_url, timeout=5)
        response.raise_for_status()
        if "Disallow: /" in response.text:
            print(f"⛔ Scraping is not allowed for {url}")
            return False
    except requests.RequestException:
        pass  # If robots.txt is inaccessible, assume scraping is allowed

    return True


def fetch_text_from_url(url: str):
    """Fetches and extracts text content from any webpage, including linked pages (Depth = 1)."""
    if not is_scrapable(url):
        raise HTTPException(status_code=403, detail="Scraping is disallowed by robots.txt")

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        # Ensure content is HTML (avoid scraping PDFs, JSON, etc.)
        if "text/html" not in response.headers.get("Content-Type", ""):
            raise HTTPException(status_code=400, detail="Unsupported content type. Only HTML pages can be scraped.")
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract only paragraph text
    main_text = " ".join([p.get_text() for p in soup.find_all("p")])

    # Extract additional links (Depth = 1)
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    links = [urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True) if a["href"].startswith("/")]

    for link in links[:3]:  # Limit recursion to avoid excessive crawling
        try:
            response = requests.get(link, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            sub_soup = BeautifulSoup(response.text, "html.parser")
            main_text += " " + " ".join([p.get_text() for p in sub_soup.find_all("p")])
        except requests.RequestException:
            continue  # Skip link if inaccessible

    return main_text


def chunk_text(text, chunk_size=512):
    """Splits extracted text into smaller, manageable chunks."""
    return [text[i: i + chunk_size] for i in range(0, len(text), chunk_size)]


@app.get("/")
async def root():
    """Root endpoint - Welcome message."""
    return {"message": "FastAPI Web Scraper is Running!"}


@app.post("/url-parser")
async def url_parser(payload: URLInput):
    """Extracts text from any website, generates embeddings, and stores them in ChromaDB."""
    print(f"🔍 Fetching text from: {payload.url} ...")
    text = fetch_text_from_url(payload.url)

    print(f"📌 Extracted {len(text)} characters of text. Chunking...")
    chunks = chunk_text(text)

    print(f"🧠 Generating embeddings for {len(chunks)} chunks...")
    embeddings = [embedding_model.encode(chunk).tolist() for chunk in chunks]

    print(f"💾 Storing embeddings in ChromaDB...")
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            metadatas=[{"source": payload.url}],
            ids=[f"{payload.url}_{i}"]
        )

    print(f"✅ Scraping completed for: {payload.url} | Chunks stored: {len(chunks)}")

    return {
        "message": "✅ Web scraping is completed successfully!",
        "url": payload.url,
        "chunks_stored": len(chunks)
    }


@app.post("/query")
async def query_embeddings(payload: QueryInput):
    """Searches stored embeddings and returns relevant text along with an AI-generated response."""
    print(f"🔎 Processing query: {payload.query} ...")
    query_embedding = embedding_model.encode(payload.query).tolist()
    
    results = collection.query(query_embeddings=[query_embedding], n_results=3)

    if not results["documents"] or not results["documents"][0]:
        print("⚠️ No relevant results found!")
        raise HTTPException(status_code=404, detail="No relevant results found.")

    retrieved_text = " ".join(results["documents"][0])
    print(f"📌 Retrieved relevant text from stored embeddings.")

    print(f"🤖 Generating response using AI model...")
    response = generator(
        f"Answer this: {payload.query} Context: {retrieved_text}",
        max_length=170,
        truncation=True
    )[0]["generated_text"]

    return {
        "query": payload.query,
        "retrieved_context": retrieved_text,
        "response": response
    }


@app.on_event("shutdown")
async def delete_chroma_db():
    """Deletes the ChromaDB database after the program exits."""
    if os.path.exists(DB_PATH):
        print(f"🗑️ Deleting ChromaDB database at {DB_PATH}...")
        shutil.rmtree(DB_PATH, ignore_errors=True)
        print("✅ ChromaDB deleted successfully.")


# Start Uvicorn in Jupyter Notebook
uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

# curl -X 'POST' 'http://127.0.0.1:8000/url-parser' \
#     -H 'Content-Type: application/json' \
#     -d '{"url": "https://en.wikipedia.org/wiki/Retrieval-augmented_generation"}'

#curl -X 'POST' 'http://127.0.0.1:8000/query' \
#     -H 'Content-Type: application/json' \
#     -d '{"query": "What are RAG ?"}'
