# **FastAPI Web Scraper with Vector Search (ChromaDB + Hugging Face Models)**  

### **📌 Overview**  
This FastAPI-based server extracts and processes content from any external URL, generates vector embeddings, and provides a queryable system using **ChromaDB** and **Hugging Face models**.  

### **🚀 Features**  
✅ **Scrape Any Website** – Extracts text from any URL (supports Depth = 1 recursion).  
✅ **Stores Data in ChromaDB** – Uses **`all-MiniLM-L6-v2`** embeddings for efficient search.  
✅ **AI-Powered Querying** – Retrieves relevant text and generates responses using **BART (`facebook/bart-large-cnn`)**.  
✅ **Auto-Deletes Database** – Removes ChromaDB after execution for cleanup.  
✅ **Optimized for Production** – Works seamlessly on **local machines or cloud servers**.  

---

## **📂 Project Structure**  
```
📁 fastapi-web-scraper
│── assign.py                 # FastAPI server with scraping & query endpoints
│── requirements.txt        # Dependencies for easy installation
│── README.md               # Documentation (this file)
│── .gitignore              # Ignore database & environment files
└── chroma_db/              # Vector database (created at runtime)
```

---

## **📌 Installation & Setup**  

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/fastapi-web-scraper.git
cd fastapi-web-scraper
```

### **2️⃣ Create a Virtual Environment**  
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### **3️⃣ Install Dependencies**  
```bash
pip install -r requirements.txt
```

---

## **🚀 Running the FastAPI Server**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
🔗 **Visit the API documentation:**  
📜 Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
📜 ReDoc UI → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)  

---

## **🛠 API Endpoints**  

### **1️⃣ `/url-parser` (POST) – Scrape a Website**  
**🔹 Description:**  
Extracts text from a webpage (including Depth = 1 links), converts it into vector embeddings, and stores it in **ChromaDB**.  

**🔹 Example Request (JSON Body):**
```json
{
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
}
```
**🔹 Example Response:**  
```json
{
  "message": "✅ Web scraping is completed successfully!",
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
  "chunks_stored": 10
}
```

**🔹 CURL Command:**  
```bash
curl -X 'POST' 'http://127.0.0.1:8000/url-parser' \
     -H 'Content-Type: application/json' \
     -d '{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}'
```

---

### **2️⃣ `/query` (POST) – Search & Get AI Response**  
**🔹 Description:**  
Searches stored embeddings for relevant text and generates an **AI-powered response** based on context.  

**🔹 Example Request (JSON Body):**  
```json
{
  "query": "What is Artificial Intelligence?"
}
```
**🔹 Example Response:**  
```json
{
  "query": "What is Artificial Intelligence?",
  "retrieved_context": "Artificial intelligence (AI) is the intelligence of machines or software...",
  "response": "Artificial intelligence refers to the simulation of human intelligence in machines..."
}
```

**🔹 CURL Command:**  
```bash
curl -X 'POST' 'http://127.0.0.1:8000/query' \
     -H 'Content-Type: application/json' \
     -d '{"query": "What is Artificial Intelligence?"}'
```

---

## **🔍 How It Works**
1. **Scraping & Processing:**
   - Extracts webpage text and linked pages (**Depth = 1**).
   - Splits text into **512-character chunks**.
   - Converts chunks into **vector embeddings** (`all-MiniLM-L6-v2`).
   - Stores embeddings in **ChromaDB**.

2. **Querying & AI Response:**
   - Converts the **query into an embedding**.
   - Searches **ChromaDB for the most relevant stored text**.
   - Uses **Hugging Face's BART model** to generate an answer.

---

## **📌 Error Handling**
| **Error** | **Possible Cause** | **Solution** |
|-----------|------------------|-------------|
| `"Scraping is disallowed by robots.txt"` | The website blocks scrapers | Use a different website or check if the site has an API |
| `"Attempt to write a readonly database"` | ChromaDB is in a protected folder | Run `chmod -R 777 chroma_db` (Linux/macOS) or move it to `/tmp/` |
| `"No relevant results found"` | Query doesn't match stored embeddings | Try a different query |

---

## **🗑️ Auto-Delete ChromaDB After Execution**
To prevent unnecessary storage, **ChromaDB is deleted after execution** using FastAPI's shutdown event:
```python
@app.on_event("shutdown")
async def delete_chroma_db():
    """Deletes the ChromaDB database after the program exits."""
    if os.path.exists(DB_PATH):
        print(f"🗑️ Deleting ChromaDB database at {DB_PATH}...")
        shutil.rmtree(DB_PATH, ignore_errors=True)
        print("✅ ChromaDB deleted successfully.")
```
✅ This ensures **no leftover data after execution**.

---  

🚀 Happy coding! 😊
