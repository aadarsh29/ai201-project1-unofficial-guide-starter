"""
pipeline.py
Milestones 3 & 4: Document Pipeline + Embedding + Retrieval
UMass Unofficial Guide RAG System

Pipeline stages:
  1. Load .txt files from docs/
  2. Clean each document
  3. Chunk by "---" separator
  4. Embed chunks with all-MiniLM-L6-v2
  5. Store in ChromaDB vector store
  6. Retrieve top-k chunks for a query
"""

import os
import re
import random
from sentence_transformers import SentenceTransformer
import chromadb


# ─── STAGE 1: LOAD DOCUMENTS ───────────────────────────────────────────────

def load_documents(docs_dir="docs"):
    """
    Load all .txt files from the docs/ directory.
    Returns a list of dicts with keys: 'source' and 'text'.
    """
    documents = []
    for filename in os.listdir(docs_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(docs_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()
            documents.append({
                "source": filename,
                "text": raw_text
            })
            print(f"  Loaded: {filename} ({len(raw_text)} characters)")
    return documents


# ─── STAGE 2: CLEAN DOCUMENTS ──────────────────────────────────────────────

def clean_document(text):
    """
    Clean a document by removing metadata headers, decorator lines,
    and boilerplate. Keeps review content, ratings, professor/course context.
    """
    text = text.replace("&amp;", "&")
    text = text.replace("&nbsp;", " ")
    text = text.replace("&#39;", "'")
    text = re.sub(r"^={3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ─── STAGE 3: CHUNK DOCUMENTS ──────────────────────────────────────────────

def chunk_document(doc):
    """
    Split a document into chunks using the '---' separator.
    Each chunk = one review block, self-contained.
    Attaches source filename and professor context to each chunk.
    """
    text = doc["text"]
    source = doc["source"]
    current_context = ""
    chunks = []
    raw_chunks = text.split("---")

    for raw_chunk in raw_chunks:
        chunk = raw_chunk.strip()

        if not chunk:
            continue

        if "PROFESSOR:" in chunk:
            match = re.search(r"PROFESSOR:\s*(.+)", chunk)
            if match:
                current_context = match.group(1).strip()
            continue

        if chunk.startswith("[DOCUMENT METADATA]"):
            continue

        if len(chunk) < 30:
            continue

        chunks.append({
            "source": source,
            "context": current_context,
            "text": chunk
        })

    return chunks


# ─── STAGE 4: EMBED + STORE IN CHROMADB ────────────────────────────────────

def embed_and_store(all_chunks, collection_name="umass_reviews"):
    """
    Embed all chunks using all-MiniLM-L6-v2 and store in ChromaDB.
    Each chunk is stored with its text, embedding, and metadata
    (source filename, professor context, chunk index).
    Returns the ChromaDB collection and model.
    """
    print("\n  Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("  Embedding chunks...")
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    print("  Storing in ChromaDB...")
    client = chromadb.Client()

    # Delete collection if it already exists (useful when re-running)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(collection_name)

    collection.add(
        ids=[f"chunk_{i}" for i in range(len(all_chunks))],
        embeddings=[embedding.tolist() for embedding in embeddings],
        documents=texts,
        metadatas=[
            {
                "source": chunk["source"],
                "context": chunk["context"],
                "chunk_index": i
            }
            for i, chunk in enumerate(all_chunks)
        ]
    )

    print(f"  Stored {collection.count()} chunks in ChromaDB.")
    return collection, model


# ─── STAGE 5: RETRIEVAL ────────────────────────────────────────────────────

def retrieve(query, collection, model, top_k=5):
    """
    Embed a query and retrieve the top-k most similar chunks from ChromaDB.
    Returns a list of results with text, metadata, and distance scores.
    """
    query_embedding = model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "text": results["documents"][0][i],
            "source": results["source"] if "source" in results else results["metadatas"][0][i]["source"],
            "context": results["metadatas"][0][i]["context"],
            "distance": results["distances"][0][i]
        })

    return retrieved


def print_retrieval_results(query, results):
    """
    Pretty-print retrieval results for a query.
    """
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")
    for i, result in enumerate(results, 1):
        print(f"\n  Result {i}")
        print(f"  Source:   {result['source']}")
        print(f"  Context:  {result['context']}")
        print(f"  Distance: {result['distance']:.4f}")
        print(f"  Text:\n  {result['text'][:300]}")
        if len(result['text']) > 300:
            print("  [truncated...]")


# ─── MAIN ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("UMass Unofficial Guide — Document Pipeline")
    print("=" * 60)

    # Stage 1: Load
    print("\n[Stage 1] Loading documents...")
    documents = load_documents(docs_dir="docs")
    print(f"  Total documents loaded: {len(documents)}")

    # Stage 2: Clean
    print("\n[Stage 2] Cleaning documents...")
    for doc in documents:
        doc["text"] = clean_document(doc["text"])
    print("  Cleaning complete.")

    # Stage 3: Chunk
    print("\n[Stage 3] Chunking documents...")
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        print(f"  {doc['source']}: {len(chunks)} chunks")
        all_chunks.extend(chunks)
    print(f"\n  Total chunks: {len(all_chunks)}")

    if len(all_chunks) < 50:
        print("  WARNING: Fewer than 50 chunks — chunks may be too large.")
    elif len(all_chunks) > 2000:
        print("  WARNING: More than 2000 chunks — chunks may be too small.")
    else:
        print("  Chunk count looks healthy.")

    # Stage 4: Embed + Store
    print("\n[Stage 4] Embedding and storing chunks...")
    collection, model = embed_and_store(all_chunks)

    # Stage 5: Test Retrieval with 3 evaluation queries
    print("\n[Stage 5] Testing retrieval...")

    test_queries = [
    "Is David Hamilton a good professor for physics 151?",
    "Which BIO 151 professor should I avoid?",
    "What is the workload like for CICS 160 with Professor Davila?",
    ]

    for query in test_queries:
        results = retrieve(query, collection, model, top_k=5)
        print_retrieval_results(query, results)

    return collection, model, all_chunks


if __name__ == "__main__":
    main()