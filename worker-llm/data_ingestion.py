"""
Data Ingestion Script for RAG Knowledge Base.
Run this once to populate your Redis vector store with documents.
"""

import os
import argparse
from pathlib import Path
from typing import List

from langchain_community.vectorstores.redis import Redis
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    DirectoryLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
)


class DataIngestion:
    """Handles loading, splitting, and storing documents for RAG."""

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))

        # Initialize components
        self.embeddings = OllamaEmbeddings(model=self.embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

    def load_documents_from_directory(self, directory_path: str) -> List[Document]:
        """Load documents from a directory with various file types."""
        print(f"📁 Loading documents from: {directory_path}")

        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        documents = []

        # Define file type loaders
        loaders = {
            "*.txt": TextLoader,
            "*.md": UnstructuredMarkdownLoader,
            "*.html": UnstructuredHTMLLoader,
            "*.htm": UnstructuredHTMLLoader,
            "*.pdf": PyPDFLoader,
        }

        # Load documents by file type
        for pattern, loader_class in loaders.items():
            try:
                loader = DirectoryLoader(
                    str(directory),
                    glob=pattern,
                    loader_cls=loader_class,
                    show_progress=True
                )
                docs = loader.load()
                documents.extend(docs)
                print(f"✅ Loaded {len(docs)} {pattern} files")
            except Exception as e:
                print(f"⚠️ Warning: Could not load {pattern} files: {e}")

        print(f"📚 Total documents loaded: {len(documents)}")
        return documents

    def load_sample_documents(self) -> List[Document]:
        """Load sample documents for testing."""
        print("📝 Loading sample documents...")

        sample_docs = [
            Document(
                page_content="TinyLlama is a compact 1.1B parameter language model trained on 3 trillion tokens. It's designed to be efficient and fast while maintaining good performance on various NLP tasks.",
                metadata={"source": "sample", "topic": "llm"}
            ),
            Document(
                page_content="Redis Stack combines the speed of Redis with modern data models like JSON, Graph, and Vector Search. It's perfect for building real-time applications with complex data requirements.",
                metadata={"source": "sample", "topic": "database"}
            ),
            Document(
                page_content="LangChain Expression Language (LCEL) allows developers to compose complex chains from simple, reusable components. It provides a declarative way to build AI applications.",
                metadata={"source": "sample", "topic": "framework"}
            ),
            Document(
                page_content="RAG (Retrieval-Augmented Generation) combines the power of information retrieval with language generation. It allows models to access external knowledge and provide more accurate, up-to-date responses.",
                metadata={"source": "sample", "topic": "ai"}
            ),
            Document(
                page_content="Vector databases store and search high-dimensional vectors efficiently. They're essential for semantic search, recommendation systems, and RAG applications.",
                metadata={"source": "sample", "topic": "database"}
            ),
            Document(
                page_content="Semantic caching stores previous queries and responses based on semantic similarity. It dramatically improves response times for similar questions without regenerating responses.",
                metadata={"source": "sample", "topic": "optimization"}
            ),
        ]

        print(f"✅ Loaded {len(sample_docs)} sample documents")
        return sample_docs

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        print(f"✂️ Splitting {len(documents)} documents into chunks...")

        split_docs = self.text_splitter.split_documents(documents)

        print(f"✅ Created {len(split_docs)} chunks")
        return split_docs

    def ingest_to_redis(self, documents: List[Document], index_name: str = "rag_documents"):
        """Ingest documents into Redis vector store."""
        print(
            f"💾 Ingesting {len(documents)} documents to Redis index: {index_name}")

        try:
            # Create or connect to Redis vector store
            vectorstore = Redis.from_documents(
                documents=documents,
                embedding=self.embeddings,
                redis_url=self.redis_url,
                index_name=index_name,
            )

            print(f"✅ Successfully ingested documents to Redis")
            print(f"📊 Index: {index_name}")
            print(f"🔗 Redis URL: {self.redis_url}")

        except Exception as e:
            print(f"❌ Error ingesting to Redis: {e}")
            raise

    def run_ingestion(self, directory_path: str = None, use_samples: bool = False):
        """Run the complete ingestion pipeline."""
        print("🚀 Starting data ingestion...")

        try:
            # Load documents
            if use_samples:
                documents = self.load_sample_documents()
            elif directory_path:
                documents = self.load_documents_from_directory(directory_path)
            else:
                print("❌ Please specify either --directory or --samples")
                return

            # Split documents
            split_docs = self.split_documents(documents)

            # Ingest to Redis
            self.ingest_to_redis(split_docs)

            print("🎉 Data ingestion completed successfully!")

        except Exception as e:
            print(f"❌ Ingestion failed: {e}")
            raise


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Ingest documents for RAG knowledge base")
    parser.add_argument(
        "--directory",
        type=str,
        help="Directory path containing documents to ingest"
    )
    parser.add_argument(
        "--samples",
        action="store_true",
        help="Use sample documents for testing"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Chunk size for text splitting (default: 500)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Chunk overlap for text splitting (default: 50)"
    )

    args = parser.parse_args()

    # Set environment variables from args
    os.environ["CHUNK_SIZE"] = str(args.chunk_size)
    os.environ["CHUNK_OVERLAP"] = str(args.chunk_overlap)

    # Run ingestion
    ingestion = DataIngestion()
    ingestion.run_ingestion(
        directory_path=args.directory,
        use_samples=args.samples
    )


if __name__ == "__main__":
    main()
