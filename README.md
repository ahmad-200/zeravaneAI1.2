# ⚡ ZeravaneAI — Web Data UNLOCKED

ZeravaneAI is a production-grade Retrieval-Augmented Generation (RAG) developer agent built for the **Bright Data × Lablab.ai Web Data UNLOCKED Hackathon 2026**. It eliminates static LLM context windows by dynamically ingesting live public web data through Bright Data's web intelligence infrastructure, indexing it via ChromaDB, and querying it with Gemini 2.5 Flash.

🚀 **Team:** Singleton Vanguard | **Developer:** Franklin Josva

---

## 🔥 Key Technical Innovations

* **3-Tier Resilient Scraping Architecture:** Automatically cascades through Bright Data Web Unlocker → SERP API → Standard requests fallback — guaranteeing data retrieval even under bot detection, geo-blocks, or CAPTCHAs.
* **Dynamic Prompt & Persona Switching:** Evaluates runtime state and pivots between a *Web-Aware Real-Time Agent* (when live context is retrieved) and a *Premium Core Programming Assistant* (when running purely on base weights).
* **Streamed 2MB-Capped Ingestion:** High-performance scraping with decoupled response stream capped at 2MB to prevent memory spikes and optimize latency.
* **Session URL Caching:** Re-querying the same URL skips re-scraping and reuses the existing ChromaDB collection — dramatically reducing API calls and latency.
* **Persistent Context Indexing:** ChromaDB embeddings with dynamic collection wipes and multi-chunk overlapping partitions (3000 chars max, 300-char rolling overlap).
* **Granular Context Auditor UI:** Built-in transparency panel showing the exact raw context payload injected into Gemini, providing a clear auditing path for every response.

---

## 🛠️ Architecture & Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit (wide layout) |
| LLM | Google Gemini 2.5 Flash |
| Vector DB | ChromaDB (persistent) |
| Web Scraping | Bright Data Web Unlocker + SERP API + BeautifulSoup4 |
| REST API | FastAPI + Uvicorn |
| Env Management | python-dotenv |

---

## 📂 Quick Start

### 1. Clone and install

```bash
git clone https://github.com/franklinjosva2605-dot/CODEMINDF.git
cd CODEMINDF
pip install -r requirements.txt
```

### 2. Set up credentials

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
# Bright Data (https://brightdata.com/cp/zones)
BRIGHT_DATA_USERNAME=your_bright_data_email@example.com
BRIGHT_DATA_PASSWORD=your_bright_data_zone_password
BRIGHT_DATA_API_KEY=your_bright_data_api_key_uuid

# Google Gemini (https://aistudio.google.com/app/apikey)
GOOGLE_API_KEY=your_google_api_key
```

> **Note:** Bright Data credentials are optional — the app runs in Demo Mode with standard requests if not set.

### 3. Run the Streamlit app

```bash
streamlit run frontend/app.py
```

### 4. (Optional) Run the REST API

```bash
uvicorn backend.api:app --reload
# Docs at http://127.0.0.1:8000/docs
```

---

## 🔐 Security Notes

- **Never commit `.env`** — it is listed in `.gitignore`.
- Use `.env.example` as the template for collaborators.
- Bright Data proxy connections use `verify=False` (required for SSL interception at the proxy level); SSL warnings are suppressed internally via `urllib3`.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/health` | Engine status + cache info |
| `POST` | `/scrape` | Scrape & index a URL |
| `POST` | `/query` | Query with optional live URL context |
| `DELETE` | `/cache` | Clear URL cache + ChromaDB collection |

Full interactive docs at `/docs` when running the API.

---

## 🏗️ Project Structure

```
zeravaneAI/
├── backend/
│   ├── engine.py        # ZeravaneEngine — core RAG + scraping pipeline
│   └── api.py           # FastAPI REST interface
├── frontend/
│   └── app.py           # Streamlit UI
├── .env                 # Your credentials (gitignored)
├── .env.example         # Credential template
├── requirements.txt
└── README.md
```

---

*Built by Franklin Josva | Team Singleton Vanguard | Bright Data × Lablab.ai 2026*
