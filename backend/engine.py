import os
import re
import warnings
import requests
import urllib3
from bs4 import BeautifulSoup
import chromadb
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()

# Suppress SSL warnings from Bright Data proxy interception
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ZeravaneEngine:
    """
    ZeravaneAI Core Engine — Web Data UNLOCKED Edition
    Built for Bright Data x Lablab.ai Hackathon 2026
    Team: Singleton Vanguard | Developer: Franklin Josva

    Features:
    - Bright Data Web Unlocker integration (bypasses bot detection, CAPTCHAs, geo-blocks)
    - Bright Data SERP API for query-based research
    - Resilient 3-tier scraping fallback architecture
    - Enhanced RAG pipeline with ChromaDB persistent vector store
    - Session-aware URL caching (avoids redundant re-scraping)
    """

    BRIGHT_DATA_HOST = "brd.superproxy.io"
    BRIGHT_DATA_PORT = 22225
    MIN_TEXT_LENGTH = 100  # Minimum chars to consider a scrape valid

    def __init__(self, chroma_path="./chroma_db"):
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)

        # Bright Data credentials from .env
        self.bd_username = os.environ.get("BRIGHT_DATA_USERNAME", "")
        self.bd_password = os.environ.get("BRIGHT_DATA_PASSWORD", "")
        self.bd_api_key = os.environ.get("BRIGHT_DATA_API_KEY", self.bd_password)
        self.bd_enabled = bool(self.bd_username and self.bd_password)

        # Session cache: avoid re-scraping the same URL repeatedly
        self._cached_url = None
        self._cached_collection = "zeravane_cache"

    # ── Proxy helpers ──────────────────────────────────────────────────────────

    def _get_bright_data_proxy(self, zone: str = "residential") -> dict:
        """Build Bright Data proxy config for the given zone."""
        proxy_url = (
            f"http://{self.bd_username}-zone-{zone}:"
            f"{self.bd_password}@{self.BRIGHT_DATA_HOST}:{self.BRIGHT_DATA_PORT}"
        )
        return {"http": proxy_url, "https": proxy_url}

    # ── Scraping tiers ─────────────────────────────────────────────────────────

    def scrape_with_bright_data_unlocker(self, url: str) -> str:
        """
        TIER 1: Bright Data Web Unlocker.
        Bypasses bot detection, CAPTCHAs, and geo-blocks automatically.
        Handles JavaScript-rendered pages via headless browser injection.
        """
        try:
            proxies = self._get_bright_data_proxy(zone="unlocker")
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                verify=False,   # Required — Bright Data intercepts SSL at proxy level
                timeout=30,
                stream=True,
            )
            # Cap response at 2MB to prevent memory spikes
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > 2 * 1024 * 1024:
                    break

            if response.status_code == 200:
                soup = BeautifulSoup(content.decode("utf-8", errors="ignore"), "html.parser")
                for el in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                    el.extract()
                text = re.sub(r"\s+", " ", soup.get_text(separator=" ")).strip()
                return text
            return f"Error: Bright Data Web Unlocker returned status {response.status_code}"
        except Exception as e:
            return f"BrightData_Error: {str(e)}"

    def scrape_with_bright_data_serp(self, query: str) -> str:
        """
        TIER 2: Bright Data SERP API.
        Real-time structured Google search results for query-based research.
        """
        try:
            serp_url = "https://api.brightdata.com/serp/google"
            headers = {
                "Authorization": f"Bearer {self.bd_api_key}",
                "Content-Type": "application/json",
            }
            payload = {"q": query, "num": 5, "hl": "en", "gl": "us"}
            response = requests.post(serp_url, json=payload, headers=headers, timeout=20)
            if response.status_code == 200:
                data = response.json()
                results = data.get("organic", [])
                snippets = [
                    f"{r.get('title', '')}: {r.get('snippet', '')}"
                    for r in results[:5]
                ]
                return " | ".join(snippets)
            return f"SERP_Error: Status {response.status_code}"
        except Exception as e:
            return f"SERP_Error: {str(e)}"

    def scrape_fallback(self, url: str) -> str:
        """
        TIER 3: Standard requests fallback.
        Used for local development and demo without Bright Data credentials.
        """
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            }
            response = requests.get(
                url,
                headers=headers,
                timeout=15,
                stream=True,
            )
            # Cap at 2MB
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > 2 * 1024 * 1024:
                    break

            if response.status_code != 200:
                return f"Error: Request failed with status {response.status_code}"

            soup = BeautifulSoup(content.decode("utf-8", errors="ignore"), "html.parser")
            for el in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                el.extract()
            text = re.sub(r"\s+", " ", soup.get_text(separator=" ")).strip()
            return text
        except Exception as e:
            return f"Fallback_Error: {str(e)}"

    def scrape_live_url(self, url: str) -> tuple:
        """
        3-Tier Resilient Scraping Architecture:
          1. Bright Data Web Unlocker (bot-proof, JS-capable, 2MB cap)
          2. Bright Data SERP API (query-based fallback)
          3. Standard requests (local dev fallback)

        Returns: (scraped_text, scrape_method_used)
        """
        _error_prefixes = ("Error:", "BrightData_Error:", "Fallback_Error:", "SERP_Error:")

        if self.bd_enabled:
            # Tier 1
            result = self.scrape_with_bright_data_unlocker(url)
            if result and not any(result.startswith(p) for p in _error_prefixes):
                return result, "🔵 Bright Data Web Unlocker"

            # Tier 2 — SERP on domain docs query
            domain = re.sub(r"https?://", "", url).split("/")[0]
            result = self.scrape_with_bright_data_serp(f"site:{domain} documentation")
            if result and not any(result.startswith(p) for p in _error_prefixes):
                return result, "🟡 Bright Data SERP API"

        # Tier 3
        result = self.scrape_fallback(url)
        return result, "⚪ Standard Requests (No Bright Data)"

    # ── RAG helpers ────────────────────────────────────────────────────────────

    def chunk_text(self, text: str, max_chars: int = 3000, overlap: int = 300) -> list:
        """Split text into overlapping chunks for vector indexing."""
        if len(text) <= max_chars:
            return [text]
        chunks, start = [], 0
        while start < len(text):
            chunks.append(text[start: start + max_chars])
            start += max_chars - overlap
        return chunks

    def refresh_vector_index(self, collection_name: str, text_chunks: list) -> bool:
        """Wipe and rebuild the ChromaDB collection with new chunks."""
        try:
            try:
                self.chroma_client.delete_collection(name=collection_name)
            except Exception:
                pass
            collection = self.chroma_client.create_collection(name=collection_name)
            collection.add(
                documents=text_chunks,
                ids=[f"chunk_{i}" for i in range(len(text_chunks))],
                metadatas=[{"index": i} for i in range(len(text_chunks))],
            )
            return True
        except Exception as e:
            print(f"[ZeravaneEngine] Vector index error: {e}")
            return False

    def query_vector_context(
        self, collection_name: str, query: str, n_results: int = 3
    ) -> str:
        """Retrieve the top-N most relevant chunks from ChromaDB."""
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
            # FIX: clamp n_results to actual chunk count to avoid ChromaDB error
            available = collection.count()
            if available == 0:
                return ""
            n = min(n_results, available)
            results = collection.query(query_texts=[query], n_results=n)
            docs = []
            if results and "documents" in results:
                for sublist in results["documents"]:
                    docs.extend(sublist)
            return "\n\n".join(docs)
        except Exception as e:
            print(f"[ZeravaneEngine] Vector query error: {e}")
            return ""

    # ── Main pipeline ──────────────────────────────────────────────────────────

    def execute_live_agent_query(
        self, user_query: str, target_url: str = None, force_rescrape: bool = False
    ) -> tuple:
        """
        Full RAG pipeline with Bright Data web intelligence layer.

        URL caching: if the same URL is queried again, skips re-scraping
        and re-uses the existing ChromaDB collection.

        Returns: (response_text, context_payload, scrape_method)
        """
        context_payload = ""
        collection_id = self._cached_collection
        scrape_method = "N/A"
        _error_prefixes = ("Error:", "BrightData_Error:", "Fallback_Error:", "SERP_Error:")

        if target_url:
            url_changed = target_url != self._cached_url

            if url_changed or force_rescrape:
                # New URL — scrape and re-index
                raw_web_data, scrape_method = self.scrape_live_url(target_url)

                scrape_ok = (
                    raw_web_data
                    and len(raw_web_data) >= self.MIN_TEXT_LENGTH
                    and not any(raw_web_data.startswith(p) for p in _error_prefixes)
                )

                if scrape_ok:
                    data_chunks = self.chunk_text(raw_web_data)
                    indexed = self.refresh_vector_index(
                        collection_name=collection_id, text_chunks=data_chunks
                    )
                    if indexed:
                        self._cached_url = target_url  # cache only on success
                        context_payload = self.query_vector_context(
                            collection_name=collection_id, query=user_query
                        )
                    else:
                        context_payload = "[Indexing Error: Could not build vector index]"
                else:
                    context_payload = f"[Scraping Warning: {raw_web_data}]"
            else:
                # Same URL — reuse existing ChromaDB collection
                scrape_method = "✅ Cache Hit (URL unchanged)"
                context_payload = self.query_vector_context(
                    collection_name=collection_id, query=user_query
                )

        # Dynamic persona switching
        web_context_available = (
            target_url
            and context_payload
            and not context_payload.startswith("[")
        )

        if web_context_available:
            system_instruction = (
                "You are ZeravaneAI, an advanced real-time web-aware developer agent powered by "
                "Bright Data's web intelligence infrastructure. Analyze the live web documentation "
                "data provided to solve the user's problem with precision. Prioritize live context "
                "over training data. Provide clean, production-ready code solutions and detailed "
                "explanations. Always cite when your answer draws from the provided documentation."
            )
        else:
            system_instruction = (
                "You are ZeravaneAI, a premium core programming assistant with deep knowledge "
                "across all major languages, frameworks, and architectures. Provide expert-level "
                "solutions, best-practice guidance, and thoroughly tested code patterns with clear "
                "explanations."
            )

        prompt_structure = (
            f"--- SYSTEM OVERVIEW ---\n"
            f"Bright Data Integration: {'Active' if self.bd_enabled else 'Demo Mode'}\n"
            f"Scrape Method: {scrape_method}\n"
            f"Context Available: {'Yes' if web_context_available else 'No'}\n\n"
            f"--- LIVE WEB DOCUMENTATION (via Bright Data) ---\n"
            f"{context_payload if context_payload else 'No web documentation retrieved.'}\n\n"
            f"--- DEVELOPER QUERY ---\n"
            f"{user_query}\n"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_structure,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                ),
            )
            return response.text, context_payload, scrape_method
        except Exception as e:
            return f"Inference error: {str(e)}", context_payload, scrape_method
