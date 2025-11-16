import os
import sys

try:
    from sentence_transformers import SentenceTransformer

    # Pre-download the models to cache them in the container
    # Lightweight model (~60MB) - using a more stable model
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"⏳ Downloading embedding model {model_name}...")
    model = SentenceTransformer(model_name)
    print("✅ Model downloaded successfully!")

    # Verify it works
    test_text = "This is a test sentence"
    embedding = model.encode(test_text)
    print(f"✓ Generated embedding of size {len(embedding)}")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This is expected during development - models will be downloaded at runtime")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error downloading model: {e}")
    print("This is expected during development - models will be downloaded at runtime")
    sys.exit(0)
