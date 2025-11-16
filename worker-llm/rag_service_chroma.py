"""
RAG Service using ChromaDB for vector storage and similarity search.
"""

from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime, timezone
import json
import asyncio
import os
import httpx
import traceback
import numpy as np
import chromadb
from chromadb.utils import embedding_functions
import uuid


class SimpleOllamaEmbeddings:
    """Embedding client that makes direct HTTP requests to Ollama with sync/async support."""

    def __init__(self, model: str, base_url: str = None):
        self.model = model
        # Primary: Use passed base_url, fallback: OLLAMA_HOST env var, final fallback: container DNS
        self.base_url = base_url or os.getenv(
            "OLLAMA_HOST", "http://ollama:11434")
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]
        self._local_encoder = None
        print(
            f"🔌 SimpleOllamaEmbeddings initialized with base_url={self.base_url}")

    def _call_embedding_sync(self, text: str) -> List[float]:
        """Synchronous embedding call."""
        url = f"{self.base_url}/v1/embeddings"
        try:
            response = httpx.post(
                url,
                json={"model": self.model, "input": text},
                timeout=30.0
            )
            response.raise_for_status()
            payload = response.json()
            # Support multiple payload shapes: top-level 'embedding' or {'data':[{'embedding': ...}]}
            embedding = payload.get("embedding")
            if not embedding and isinstance(payload.get("data"), list) and payload["data"]:
                embedding = payload["data"][0].get("embedding")
            if not embedding:
                raise ValueError("No embedding in response")
            return embedding
        except Exception as e:
            print(f"❌ Embedding failed for text={text[:100]}... at url={url}")
            # If Ollama returned 404 (model not found), fall back to local encoder
            try:
                if hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 404:
                    print(
                        "⚠️ Ollama model not found (404) — falling back to local sentence-transformers encoder")
                    return self._local_embed_sync(text)
            except Exception:
                pass
            raise RuntimeError(f"Error from embedding endpoint: {e}")

    async def _call_embedding_async(self, text: str) -> List[float]:
        """Asynchronous embedding call."""
        url = f"{self.base_url}/v1/embeddings"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"model": self.model, "input": text},
                    timeout=30.0
                )
                response.raise_for_status()
                payload = response.json()
                embedding = payload.get("embedding")
                if not embedding and isinstance(payload.get("data"), list) and payload["data"]:
                    embedding = payload["data"][0].get("embedding")
                if not embedding:
                    raise ValueError("No embedding in response")
                return embedding
        except Exception as e:
            print(f"❌ Embedding failed for text={text[:100]}... at url={url}")
            # If Ollama returned 404 (model not found), fall back to local encoder
            try:
                if hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 404:
                    print(
                        "⚠️ Ollama model not found (404) — falling back to local sentence-transformers encoder")
                    return await asyncio.get_running_loop().run_in_executor(None, self._local_embed_sync, text)
            except Exception:
                pass
            raise RuntimeError(f"Error from embedding endpoint: {e}")

    # --- Local encoder fallback (lazy) ---
    def _load_local_encoder(self):
        if self._local_encoder is None:
            try:
                from sentence_transformers import SentenceTransformer
                print(
                    "🧠 Loading local SentenceTransformer encoder (this may take a moment)...")
                # Use a small, reasonable default to keep memory low
                self._local_encoder = SentenceTransformer(
                    'sentence-transformers/all-MiniLM-L6-v2')
                print("✅ Local encoder loaded")
            except Exception as e:
                print(f"❌ Failed to load local encoder: {e}")
                raise

    def _local_embed_sync(self, text: str) -> List[float]:
        """Synchronous fallback to sentence-transformers embeddings."""
        self._load_local_encoder()
        vec = self._local_encoder.encode(text).tolist()
        return vec


class CustomEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, ollama_embeddings: SimpleOllamaEmbeddings):
        self.ollama_embeddings = ollama_embeddings

    def __call__(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        return [self.ollama_embeddings._call_embedding_sync(text) for text in texts]


class RAGService:
    """Multi-tier RAG service using ChromaDB and vector similarity."""

    def __init__(self):
        # Configuration from environment
        self.llm_model = os.getenv("MODEL_NAME", "tinyllama")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.cache_similarity_threshold = float(
            os.getenv("RAG_CACHE_SIMILARITY_THRESHOLD", "0.85"))
        self.rag_top_k = int(os.getenv("RAG_TOP_K", "3"))
        self.rag_document_similarity_threshold = float(
            os.getenv("RAG_DOCUMENT_SIMILARITY_THRESHOLD", "0.75"))

        # Initialize embeddings
        self.embeddings = SimpleOllamaEmbeddings(
            model=self.embedding_model,
            base_url=os.getenv("OLLAMA_HOST", None)
        )

        # Track stopped sessions
        self.stopped_sessions = set()

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path="chroma_db")

        # Create embedding function
        self.ef = CustomEmbeddingFunction(self.embeddings)

        # Create collections for cache and documents
        self.cache_collection = self.chroma_client.get_or_create_collection(
            name="semantic_cache",
            embedding_function=self.ef
        )
        self.doc_collection = self.chroma_client.get_or_create_collection(
            name="documents",
            embedding_function=self.ef
        )

        # HTTP client for Ollama streaming responses
        self.http_client = httpx.AsyncClient(timeout=None)

        print("🧭 RAG Service initialized with:")
        print(f" - LLM model: {self.llm_model}")
        print(f" - Embedding model: {self.embedding_model}")
        print(f" - Cache threshold: {self.cache_similarity_threshold}")
        print(f" - RAG top k: {self.rag_top_k}")

    def update_stopped_sessions(self, stopped_sessions: set):
        """Update the stopped sessions set."""
        self.stopped_sessions = stopped_sessions.copy()

    def initialize(self):
        """Initialize ChromaDB with test documents."""
        print("\n🚀 Initializing RAG Service vector stores...")

        try:
            print("Creating semantic cache...")
            self.update_semantic_cache(
                "What is RAG?",
                "RAG (Retrieval-Augmented Generation) combines document retrieval with language model generation."
            )
            print("✅ Semantic cache vectorstore created")

            print("Creating RAG vectorstore...")
            self.add_document(
                "RAG systems enhance LLM responses by retrieving relevant context from a document store.",
                source="test",
                doc_type="definition"
            )
            print("✅ RAG vectorstore created")

            print("Creating initial test documents...")
            self._get_embedding("Test query to initialize embeddings")

        except Exception as e:
            print(f"❌ Error initializing RAG service: {e}")
            traceback.print_exc()
            raise

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text synchronously."""
        return self.embeddings._call_embedding_sync(text)

    def update_semantic_cache(self, query_text: str, response_text: str):
        """Add or update entry in semantic cache."""
        try:
            print("\n💾 Adding new entry to semantic cache...")

            id = str(uuid.uuid4())
            self.cache_collection.add(
                documents=[query_text],
                metadatas=[{
                    "response": response_text,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }],
                ids=[id]
            )

            print("✅ Added to semantic cache")

        except Exception as e:
            print(f"❌ Failed to add document to cache: {str(e)}")
            raise

    def add_document(self, text: str, source: str = None, doc_type: str = None):
        """Add document to RAG store."""
        try:
            id = str(uuid.uuid4())
            self.doc_collection.add(
                documents=[text],
                metadatas=[{
                    "source": source or "unknown",
                    "type": doc_type or "document",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }],
                ids=[id]
            )

        except Exception as e:
            print(f"❌ Failed to add document to RAG store: {str(e)}")
            raise

    def check_semantic_cache(self, query_text: str) -> Optional[str]:
        """Check semantic cache for similar queries using vector similarity."""
        try:
            print("\n🔍 Checking semantic cache for query...")

            # Query the cache collection
            results = self.cache_collection.query(
                query_texts=[query_text],
                n_results=1,
                include=["metadatas", "distances"]
            )

            if results["distances"][0]:
                # ChromaDB uses L2 distance, convert to similarity score (1 / (1 + distance))
                similarity = 1 / (1 + results["distances"][0][0])
                print(f"Cache similarity score: {similarity:.3f}")
                if similarity > self.cache_similarity_threshold:
                    print(f"✅ Found cache hit with score {similarity:.3f}")
                    return results["metadatas"][0][0]["response"]

            print("❌ No similar cached entries found")
            return None

        except Exception as e:
            print(f"❌ Error checking semantic cache: {e}")
            return None

    def get_relevant_context(self, query_text: str) -> List[str]:
        """Get relevant documents using vector similarity."""
        try:
            print("\n🔍 Finding relevant documents...")

            # Query the document collection
            results = self.doc_collection.query(
                query_texts=[query_text],
                n_results=self.rag_top_k,
                include=["documents", "distances"]
            )

            if results["documents"][0]:
                filtered_documents = []
                for i, doc in enumerate(results["documents"][0]):
                    distance = results["distances"][0][i]
                    # Convert distance to similarity score
                    similarity = 1 / (1 + distance)
                    if similarity >= self.rag_document_similarity_threshold:
                        filtered_documents.append(doc)
                    else:
                        print(
                            f"Document '{doc[:50]}...' below similarity threshold ({similarity:.3f} < {self.rag_document_similarity_threshold})")

                if filtered_documents:
                    print(
                        f"✅ Found {len(filtered_documents)} relevant documents above threshold")
                    return filtered_documents

            print("❌ No relevant documents found")
            return []

        except Exception as e:
            print(f"❌ Error finding relevant documents: {e}")
            return []

    async def process_query_streaming(self, query: str, session_id: str = None, stopped_sessions: set = None) -> AsyncGenerator[str, None]:
        """Process a query with multi-tier RAG and stream the response."""
        try:
            print(f"\n📝 Processing query: {query}")
            print(f"🔍 Session ID: {session_id}")
            print(f"🛑 Stopped sessions: {stopped_sessions}")

            # Check if already stopped before starting
            if session_id and stopped_sessions and session_id in stopped_sessions:
                print(
                    f"🛑 RAG generation already stopped for session {session_id}")
                return

            # Check semantic cache first
            cached_response = self.check_semantic_cache(query)
            if cached_response:
                print("✨ Using cached response")
                yield cached_response
                return

            # Get relevant context
            context = self.get_relevant_context(query)
            context_text = "\\n\\n".join(context) if context else ""

            # Build prompt with retrieved context
            system_prompt = (
                "You are a helpful AI assistant. Use the provided context to answer questions accurately. "
                "If the context doesn't contain relevant information, use your general knowledge but mention this fact. "
                "Keep responses concise and focused."
            )

            if context_text:
                system_prompt += f"\\n\\nContext:\\n{context_text}"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
            else:
                # If no relevant context, send the query directly without RAG context
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]

            # Call Ollama API with streaming
            url = f"{os.getenv('OLLAMA_HOST', 'http://ollama:11434')}/api/chat"
            async with self.http_client.stream(
                "POST",
                url,
                json={"model": self.llm_model,
                      "messages": messages, "stream": True}
            ) as response:
                response.raise_for_status()

                # Initialize variables for response construction
                full_response = ""
                was_stopped = False
                async for line in response.aiter_lines():
                    # Check for stop signal before processing each line
                    if session_id and stopped_sessions and session_id in stopped_sessions:
                        print(
                            f"🛑 RAG generation stopped for session {session_id} (line check)")
                        was_stopped = True
                        break

                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        if content := chunk.get("message", {}).get("content", ""):
                            # Check for stop signal before yielding each token
                            if session_id and stopped_sessions and session_id in stopped_sessions:
                                print(
                                    f"🛑 RAG generation stopped for session {session_id} (token check)")
                                was_stopped = True
                                break

                            full_response += content
                            yield content

                    except json.JSONDecodeError:
                        print(f"⚠️ Failed to parse chunk: {line}")
                        continue

            # Only update semantic cache if generation wasn't stopped
            if full_response and not was_stopped:
                self.update_semantic_cache(query, full_response)
            elif was_stopped:
                print("🚫 Skipping cache update due to stopped generation")

        except Exception as e:
            error_msg = f"❌ Error processing query: {str(e)}"
            print(error_msg)
            yield error_msg
            raise


# Global RAG service instance
rag_service = None


async def initialize_rag_service():
    """Initialize global RAG service."""
    try:
        global rag_service
        rag_service = RAGService()
        rag_service.initialize()
        print("✅ Global RAG service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize global RAG service: {str(e)}")
        raise


async def process_query_with_rag(query: str, session_id: str = None, stopped_sessions: set = None) -> AsyncGenerator[str, None]:
    """Process a query using the global RAG service."""
    try:
        async for token in rag_service.process_query_streaming(query, session_id, stopped_sessions):
            yield token
    except Exception as e:
        print(f"❌ Error in process_query_with_rag: {e}")
        yield f"Error: {str(e)}"


async def close_rag_service():
    """Close the RAG service resources."""
    if hasattr(rag_service, 'http_client'):
        await rag_service.http_client.aclose()
