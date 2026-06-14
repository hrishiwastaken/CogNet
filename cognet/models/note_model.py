import re
import hashlib

# Check if sentence-transformers is available
SENTENCE_TRANSFORMERS_AVAILABLE = None

def check_sentence_transformers():
    global SENTENCE_TRANSFORMERS_AVAILABLE
    if SENTENCE_TRANSFORMERS_AVAILABLE is not None:
        return SENTENCE_TRANSFORMERS_AVAILABLE
    try:
        from sentence_transformers import SentenceTransformer
        SENTENCE_TRANSFORMERS_AVAILABLE = True
    except ImportError:
        SENTENCE_TRANSFORMERS_AVAILABLE = False
    return SENTENCE_TRANSFORMERS_AVAILABLE

_model = None

def get_transformer_model():
    """
    Returns the initialized semantic transformer model.
    """
    global _model, SENTENCE_TRANSFORMERS_AVAILABLE
    if not check_sentence_transformers():
        return None
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print("[CogNet] Initializing local semantic model (all-MiniLM-L6-v2)...")
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            print("[CogNet] Model successfully preloaded.")
        except Exception as e:
            print(f"[CogNet] Warning: Could not initialize model: {e}")
            SENTENCE_TRANSFORMERS_AVAILABLE = False
            return None
    return _model


def split_into_sentences(text: str) -> list[str]:
    if not text:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def generate_3d_vector(sentence: str, category: str) -> list[float]:
    """
    Generates a dense vector. Uses the preloaded 384-dimensional semantic engine if available,
    otherwise falls back to the deterministic lexical-hashing algorithm.
    """
    model = get_transformer_model()
    if model is not None:
        try:
            embedding = model.encode(sentence)
            return embedding.tolist()
        except Exception as e:
            print(f"[CogNet] Core Embedding Error: {e}")
            pass
            
    # 3D Lexical Hashing(Fallback)
    cat_hash = hashlib.md5(category.lower().encode('utf-8')).digest()
    cx = ((cat_hash[0] / 255.0) - 0.5) * 6.0
    cy = ((cat_hash[1] / 255.0) - 0.5) * 6.0
    cz = ((cat_hash[2] / 255.0) - 0.5) * 6.0
    
    words = re.findall(r'\w+', sentence.lower())
    wx, wy, wz = 0.0, 0.0, 0.0
    if words:
        for w in words:
            h = hashlib.md5(w.encode('utf-8')).digest()
            wx += ((h[0] / 255.0) - 0.5) * 0.8
            wy += ((h[1] / 255.0) - 0.5) * 0.8
            wz += ((h[2] / 255.0) - 0.5) * 0.8
            
        import numpy as np
        norm = np.sqrt(wx**2 + wy**2 + wz**2) + 1e-9
        wx, wy, wz = (wx / norm) * 1.5, (wy / norm) * 1.5, (wz / norm) * 1.5

    return [float(cx + wx), float(cy + wy), float(cz + wz)]