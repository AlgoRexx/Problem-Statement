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

### **2️⃣ Ensure Python 3.9.7 is Installed (Using Conda)**  
This project requires Python 3.9.7, so set up a Conda environment.  

🔹 Step 1: Create a Conda Environment
```bash
conda create --name fastapi_scraper python=3.9.7 -y
```
🔹 Step 2: Activate the Conda Environment
```bash
conda activate fastapi_scraper
```

### **3️⃣ Install Dependencies**  
```bash
pip install -r requirements.txt
```

---

## **🚀 Running the FastAPI Server**
Instead of using Uvicorn, start the server with:  
```bash
sudo python assign.py
```
✅ This ensures the server runs with the required permissions.  

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

**🔹 cURL Command:**  
```bash
curl -X 'POST' 'http://127.0.0.1:8000/url-parser' \
     -H 'Content-Type: application/json' \
     -d '{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}'
```

**🔹 Postman Request:**  
1. Open **Postman**  
2. **Set method to `POST`**  
3. **Enter URL:**  
   ```
   http://127.0.0.1:8000/url-parser
   ```
4. **Go to "Body" tab** → Select **raw** → Choose **JSON** format.
5. **Paste this JSON:**
   ```json
   {
     "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
   }
   ```
6. Click **Send**

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

**🔹 cURL Command:**  
```bash
curl -X 'POST' 'http://127.0.0.1:8000/query' \
     -H 'Content-Type: application/json' \
     -d '{"query": "What is Artificial Intelligence?"}'
```

**🔹 Postman Request:**  
1. Open **Postman**  
2. **Set method to `POST`**  
3. **Enter URL:**  
   ```
   http://127.0.0.1:8000/query
   ```
4. **Go to "Body" tab** → Select **raw** → Choose **JSON** format.
5. **Paste this JSON:**
   ```json
   {
     "query": "What is Artificial Intelligence?"
   }
   ```
6. Click **Send**

---

## **📌 Import Postman Collection**
To make testing easier, you can **import a Postman collection** instead of manually setting everything up.

1. Open **Postman**  
2. Click **"Import"**  
3. Select **"Raw text"** and paste this JSON:  
```json
{
  "info": {
    "name": "FastAPI Scraper API",
    "_postman_id": "abcd-1234",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Scrape Website",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": { "raw": "http://127.0.0.1:8000/url-parser" },
        "body": { "mode": "raw", "raw": "{ \"url\": \"https://en.wikipedia.org/wiki/Artificial_intelligence\" }" }
      }
    },
    {
      "name": "Query Stored Data",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": { "raw": "http://127.0.0.1:8000/query" },
        "body": { "mode": "raw", "raw": "{ \"query\": \"What is Artificial Intelligence?\" }" }
      }
    }
  ]
}
```
4. Click **Import**, and both endpoints will be ready to use!
