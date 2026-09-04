import os
import re
import math
import json
import urllib.request
import urllib.error

KNOWLEDGE_DIR_1 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge")
KNOWLEDGE_DIR_2 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge")


def get_knowledge_chunks():
    """Loads and chunks knowledge text files."""
    chunks = []
    dirs_to_check = [KNOWLEDGE_DIR_1, KNOWLEDGE_DIR_2]

    loaded_files = set()
    for kdir in dirs_to_check:
        if not os.path.exists(kdir):
            continue
        for fname in os.listdir(kdir):
            if fname.endswith(".txt") and fname not in loaded_files:
                loaded_files.add(fname)
                fpath = os.path.join(kdir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Chunk by double newlines or section headers
                    raw_paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                    for i, para in enumerate(raw_paragraphs):
                        chunks.append({
                            "chunk_id": f"{fname}_chunk_{i}",
                            "source_file": fname,
                            "text": para
                        })
                except Exception as e:
                    print(f"[Retrieval] Warning: Could not read {fpath}: {e}")

    return chunks


def tokenize(text):
    """Simple alphanumeric tokenizer."""
    return set(re.findall(r"\w+", text.lower()))


def keyword_retrieval(query, chunks, top_k=3):
    """Calculates keyword/token overlap relevance score."""
    q_tokens = tokenize(query)
    if not q_tokens:
        return chunks[:top_k]

    scored = []
    for c in chunks:
        c_tokens = tokenize(c["text"])
        overlap = len(q_tokens.intersection(c_tokens))
        # Bonus for exact key phrase matches
        if any(term in c["text"].lower() for term in q_tokens if len(term) > 3):
            overlap += 1
        scored.append((overlap, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_k]]


def cosine_similarity(vec_a, vec_b):
    """Manual cosine similarity using standard library math."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def get_gemini_embedding(text):
    """Optional REST call for gemini-embedding-001 using urllib."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]}
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("embedding", {}).get("values", None)
    except Exception as e:
        print(f"[Retrieval] Embedding REST call skipped: {e}")
        return None


def retrieve_relevant_context(query, top_k=2):
    """
    Main entry point for local context retrieval.
    Falls back gracefully to keyword retrieval.
    """
    chunks = get_knowledge_chunks()
    if not chunks:
        return "Standard Retail Policy: Stockouts <= 7d are High Risk; Overstock >= 90d is High Coverage."

    matched = keyword_retrieval(query, chunks, top_k=top_k)
    return "\n\n".join([f"[{m['source_file']}]: {m['text']}" for m in matched])


if __name__ == "__main__":
    ctx = retrieve_relevant_context("What is the reorder policy for stockout?")
    print("Retrieved Context:\n", ctx)
