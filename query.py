"""
query.py
Milestone 5: Grounded Generation
UMass Unofficial Guide RAG System

Wires together retrieval (pipeline.py) and generation (Groq LLM) to produce
grounded, cited answers from student review documents only.
"""

import os
from groq import Groq
from dotenv import load_dotenv
from pipeline import load_documents, clean_document, chunk_document, embed_and_store, retrieve

load_dotenv()

# ─── SYSTEM PROMPT ─────────────────────────────────────────────────────────
# This is the most important part — it enforces grounding.
# The LLM is explicitly told to answer ONLY from the provided context.

SYSTEM_PROMPT = """You are a helpful assistant for UMass Amherst students.
You answer questions about professors and courses using ONLY the student reviews provided to you.

Rules you must follow:
1. Answer ONLY using information from the provided review excerpts. Do not use any outside knowledge.
2. If the provided reviews do not contain enough information to answer the question, say exactly: "I don't have enough information in my documents to answer that."
3. Always cite your sources by mentioning the professor's name and course when making a claim.
4. If reviews conflict with each other, acknowledge both perspectives.
5. Be honest about the sentiment in the reviews — don't soften negative reviews or exaggerate positive ones.
"""


# ─── BUILD THE CONTEXT BLOCK ───────────────────────────────────────────────

def build_context(retrieved_chunks):
    """
    Format retrieved chunks into a readable context block for the LLM prompt.
    Each chunk includes its source file and professor context.
    """
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        context_parts.append(
            f"[Excerpt {i} — Source: {chunk['source']}, Professor: {chunk['context']}]\n"
            f"{chunk['text']}\n"
        )
    return "\n".join(context_parts)


# ─── GENERATE ANSWER ───────────────────────────────────────────────────────

def generate_answer(query, retrieved_chunks):
    """
    Send the query + retrieved context to Groq's LLM and return a grounded answer.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    context = build_context(retrieved_chunks)

    user_message = f"""Here are student reviews to use as context:

{context}

Based ONLY on the reviews above, answer this question:
{query}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,  # Low temperature = more factual, less creative
        max_tokens=600
    )

    return response.choices[0].message.content


# ─── EXTRACT SOURCES ───────────────────────────────────────────────────────

def extract_sources(retrieved_chunks):
    """
    Programmatically extract unique source + professor pairs from retrieved chunks.
    This guarantees attribution regardless of what the LLM says.
    """
    seen = set()
    sources = []
    for chunk in retrieved_chunks:
        key = (chunk["source"], chunk["context"])
        if key not in seen:
            seen.add(key)
            sources.append(f"{chunk['source']} — {chunk['context']}")
    return sources


# ─── MAIN ASK FUNCTION ─────────────────────────────────────────────────────

# Global variables to avoid reloading model/collection on every query
_collection = None
_model = None

def initialize():
    """Load documents, chunk, embed, and store. Called once at startup."""
    global _collection, _model

    print("Initializing RAG pipeline...")
    documents = load_documents(docs_dir="docs")
    for doc in documents:
        doc["text"] = clean_document(doc["text"])

    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))

    _collection, _model = embed_and_store(all_chunks)
    print(f"Ready. {len(all_chunks)} chunks loaded.\n")


def ask(question):
    """
    End-to-end RAG query:
      1. Retrieve top-5 relevant chunks
      2. Generate a grounded answer using only those chunks
      3. Return answer + programmatic source list

    Returns a dict with keys: 'answer', 'sources'
    """
    global _collection, _model

    if _collection is None or _model is None:
        initialize()

    # Retrieve
    retrieved = retrieve(question, _collection, _model, top_k=5)

    # Generate
    answer = generate_answer(question, retrieved)

    # Extract sources programmatically
    sources = extract_sources(retrieved)

    return {
        "answer": answer,
        "sources": sources
    }


# ─── CLI TEST ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    initialize()

    test_queries = [
        "Is David Hamilton a good professor for PHY 151?",
        "Which BIO 151 professor should I avoid?",
        "What is the workload like for CICS 160 with Professor Davila?",
        "What dining hall should I eat at?",  # Should trigger "I don't have enough information"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Q: {query}")
        print("="*60)
        result = ask(query)
        print(f"A: {result['answer']}")
        print(f"\nSources:")
        for source in result["sources"]:
            print(f"  • {source}")