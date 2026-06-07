"""
pipeline.py
Milestone 3: Document Ingestion and Chunking
UMass Unofficial Guide RAG System

Pipeline stages:
  1. Load .txt files from docs/
  2. Clean each document
  3. Chunk by "---" separator
  4. Inspect and validate chunks
"""

import os
import re
import random


# ─── STAGE 1: LOAD DOCUMENTS ───────────────────────────────────────────────

def load_documents(docs_dir="docs"):
    """
    Load all .txt files from the docs/ directory.
    Returns a list of dicts with keys: 'source' (filename) and 'text' (raw content).
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
    Clean a document by removing metadata headers, separator lines,
    section headers, and other boilerplate that shouldn't be embedded.
    Keeps: review content, ratings, tags, professor/course context.
    """
    # Remove the top-level document metadata block (everything before first [REVIEW or [PROFESSOR section)
    # Keep professor headers as they provide context
    
    # Remove HTML entities just in case
    text = text.replace("&amp;", "&")
    text = text.replace("&nbsp;", " ")
    text = text.replace("&#39;", "'")

    # Remove lines that are purely decorative (===... or ---...)
    # We keep --- as chunk separators so only remove === lines
    text = re.sub(r"^={3,}\s*$", "", text, flags=re.MULTILINE)

    # Normalize multiple blank lines to a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ─── STAGE 3: CHUNK DOCUMENTS ──────────────────────────────────────────────

def chunk_document(doc):
    """
    Split a document into chunks using the '---' separator.
    Each chunk = one review block, already self-contained.
    Attaches source filename and professor/course context to each chunk.
    Returns a list of dicts with keys: 'source', 'context', 'text'.
    """
    text = doc["text"]
    source = doc["source"]

    # Extract the context header (professor name + course) from section headers
    # These look like: "PROFESSOR: Cole Reilly" inside ===...=== blocks
    current_context = ""

    chunks = []
    # Split on the --- separator
    raw_chunks = text.split("---")

    for raw_chunk in raw_chunks:
        chunk = raw_chunk.strip()

        # Skip empty chunks
        if not chunk:
            continue

        # If this chunk is a professor section header (contains PROFESSOR:), 
        # update the context and skip embedding it as its own chunk
        if chunk.startswith("PROFESSOR:") or "PROFESSOR:" in chunk:
            # Extract professor name for context
            match = re.search(r"PROFESSOR:\s*(.+)", chunk)
            if match:
                current_context = match.group(1).strip()
            continue

        # Skip document metadata blocks (start with [DOCUMENT METADATA])
        if chunk.startswith("[DOCUMENT METADATA]"):
            continue

        # Skip very short chunks (less than 30 characters — likely stray separators)
        if len(chunk) < 30:
            continue

        chunks.append({
            "source": source,
            "context": current_context,
            "text": chunk
        })

    return chunks


# ─── STAGE 4: INSPECT CHUNKS ───────────────────────────────────────────────

def inspect_chunks(all_chunks, sample_size=5):
    """
    Print a random sample of chunks for manual inspection.
    Check: is each chunk readable, self-contained, and free of artifacts?
    """
    print(f"\n{'='*60}")
    print(f"CHUNK INSPECTION — {sample_size} random samples")
    print(f"{'='*60}")

    sample = random.sample(all_chunks, min(sample_size, len(all_chunks)))
    for i, chunk in enumerate(sample, 1):
        print(f"\n--- Chunk {i} ---")
        print(f"Source:  {chunk['source']}")
        print(f"Context: {chunk['context']}")
        print(f"Length:  {len(chunk['text'])} characters")
        print(f"Text:\n{chunk['text'][:400]}")  # Print first 400 chars
        if len(chunk['text']) > 400:
            print("  [truncated...]")

    print(f"\n{'='*60}")


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

    # Validate chunk count
    if len(all_chunks) < 50:
        print("  WARNING: Fewer than 50 chunks — chunks may be too large.")
    elif len(all_chunks) > 2000:
        print("  WARNING: More than 2000 chunks — chunks may be too small.")
    else:
        print("  Chunk count looks healthy.")

    # Stage 4: Inspect
    inspect_chunks(all_chunks, sample_size=5)

    return all_chunks


if __name__ == "__main__":
    main()