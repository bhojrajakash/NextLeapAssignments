# rag_engine.py
# Robust, import-safe Retrieval + Answer formatter for the SBI MF FAQ prototype.

import numpy as np

# Delay heavy imports to inside functions to avoid top-level crashes on Streamlit deploy
def _safe_tfidf_init(texts):
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words="english").fit(texts)
        doc_vectors = vectorizer.transform(texts)
        return {"vectorizer": vectorizer, "doc_vectors": doc_vectors, "ok": True}
    except Exception:
        return {"vectorizer": None, "doc_vectors": None, "ok": False}

class RAGEngine:
    """
    Simple RAG engine:
    - builds TF-IDF index if sklearn available
    - falls back to keyword matching if not
    Usage: engine = RAGEngine(corpus_list)
    corpus_list: list of dicts with keys: id, title, text, source, date
    """
    def __init__(self, corpus):
        if not isinstance(corpus, list) or len(corpus) == 0:
            raise ValueError("corpus must be a non-empty list of documents")
        self.corpus = corpus
        self.texts = [ (c.get("text","") or "") for c in corpus ]
        self._tf = _safe_tfidf_init(self.texts)
        self.use_tfidf = bool(self._tf.get("ok", False))

    def _retrieve_tfidf(self, query, top_k=1):
        q = query or ""
        qv = self._tf["vectorizer"].transform([q])
        sims = (qv @ self._tf["doc_vectors"].T).toarray().ravel()
        idxs = np.argsort(-sims)[:top_k]
        return [(self.corpus[i], float(sims[i])) for i in idxs]

    def _retrieve_keywords(self, query, top_k=1):
        q = query.lower()
        scores = []
        for c in self.corpus:
            txt = (c.get("text","") or "").lower()
            score = sum(1 for w in q.split() if w and w in txt)
            scores.append(score)
        idxs = np.argsort(-np.array(scores))[:top_k]
        return [(self.corpus[int(i)], float(scores[int(i)])) for i in idxs]

    def retrieve(self, query, top_k=1):
        if self.use_tfidf:
            return self._retrieve_tfidf(query, top_k=top_k)
        else:
            return self._retrieve_keywords(query, top_k=top_k)

    def _extract_sentence(self, doc_text, query):
        # look for a short sentence containing key tokens; fallback to first sentence
        if not doc_text:
            return ""
        sents = [s.strip() for s in doc_text.split('.') if s.strip()]
        qtokens = [t for t in (query or "").lower().split() if len(t) > 2]
        for s in sents:
            lower = s.lower()
            if any(tok in lower for tok in qtokens):
                return s
        return sents[0] if sents else doc_text

    def format_answer(self, doc, query):
        # produce <=3-sentence concise answer + single citation + last-updated
        text = doc.get("text","")
        chosen = self._extract_sentence(text, query)
        # keep <=3 sentences
        sentences = [s.strip() for s in chosen.split('.') if s.strip()]
        answer = '. '.join(sentences[:3])
        if not answer.endswith('.'):
            answer = answer
        source = doc.get("source","")
        date = doc.get("date","")
        out = f"{answer}\n\nSource: {source}\nLast updated from sources: {date}"
        return out

    def answer(self, query):
        if not query or not query.strip():
            return "Please ask a factual question about the covered schemes."
        results = self.retrieve(query, top_k=1)
        if not results:
            return "I couldn't find a factual answer in the available sources."
        doc, score = results[0]
        return self.format_answer(doc, query)
