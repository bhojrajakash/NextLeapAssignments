# rag_engine.py
# Robust RAG engine with improved extraction for numeric facts (expense ratios etc.)

import numpy as np
import re

def _safe_tfidf_init(texts):
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words="english").fit(texts)
        doc_vectors = vectorizer.transform(texts)
        return {"vectorizer": vectorizer, "doc_vectors": doc_vectors, "ok": True}
    except Exception:
        return {"vectorizer": None, "doc_vectors": None, "ok": False}

class RAGEngine:
    def __init__(self, corpus):
        if not isinstance(corpus, list) or len(corpus) == 0:
            raise ValueError("corpus must be a non-empty list of documents")
        self.corpus = corpus
        self.texts = [ (c.get("text","") or "") for c in corpus ]
        self._tf = _safe_tfidf_init(self.texts)
        self.use_tfidf = bool(self._tf.get("ok", False))

    def _retrieve_tfidf(self, query, top_k=1):
        qv = self._tf["vectorizer"].transform([query])
        sims = (qv @ self._tf["doc_vectors"].T).toarray().ravel()
        idxs = np.argsort(-sims)[:top_k]
        return [(self.corpus[i], float(sims[i])) for i in idxs]

    def _retrieve_keywords(self, query, top_k=1):
        q = (query or "").lower()
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

    def _split_sentences(self, text):
        # naive sentence splitter but keeps numeric tokens intact
        # split on period/question/exclamation followed by space and uppercase or number
        parts = re.split(r'(?<=[\.\?\!])\s+(?=[A-Z0-9])', text)
        parts = [p.strip() for p in parts if p and p.strip()]
        return parts

    def _find_sentence_with_tokens(self, text, tokens):
        tokens = [t.lower() for t in tokens if t.strip()]
        sents = self._split_sentences(text)
        for s in sents:
            low = s.lower()
            if any(tok in low for tok in tokens):
                return s
        return None

    def _find_numeric_pattern_sentence(self, text, patterns=None):
        # patterns: list of regex patterns to match numeric facts (percentages, decimals)
        if patterns is None:
            patterns = [r'\d{1,3}(?:\.\d+)?\s*%?', r'\d{1,3}(?:\.\d+)?\s*per\s*cent']
        sents = self._split_sentences(text)
        for s in sents:
            for p in patterns:
                if re.search(p, s, flags=re.IGNORECASE):
                    return s
        return None

    def format_answer(self, doc, query):
        text = doc.get("text","") or ""
        qlow = (query or "").lower()

        # Priority 1: if query mentions 'expense' or 'expense ratio', try to extract percentage precisely
        if 'expense' in qlow or 'expense ratio' in qlow or 'expense-ratio' in qlow:
            # try to find sentence containing 'expense' tokens
            sent = self._find_sentence_with_tokens(text, ['expense ratio', 'expense', 'ongoing expense', 'expense ratio (direct)'])
            if sent:
                # try to find percentage/number in that sentence
                m = re.search(r'(\d{1,3}(?:\.\d+)?\s*%|\d{1,3}(?:\.\d+)?\s*per\s*cent)', sent, flags=re.IGNORECASE)
                if m:
                    # return the entire found sentence (keeps the number)
                    answer = sent.strip()
                    source = doc.get("source","")
                    date = doc.get("date","")
                    return f"{answer}\n\nSource: {source}\nLast updated from sources: {date}"
                else:
                    # fallback: return the sentence even if no % token found
                    answer = sent.strip()
                    source = doc.get("source","")
                    date = doc.get("date","")
                    return f"{answer}\n\nSource: {source}\nLast updated from sources: {date}"

            # if no explicit expense sentence found, search for any nearby numeric match
            sent2 = self._find_numeric_pattern_sentence(text)
            if sent2:
                answer = sent2.strip()
                source = doc.get("source","")
                date = doc.get("date","")
                return f"{answer}\n\nSource: {source}\nLast updated from sources: {date}"

        # Priority 2: try to find sentence containing tokens from query
        tokens = qlow.split()
        sent = self._find_sentence_with_tokens(text, tokens[:8])  # limit token set
        if sent:
            answer = sent.strip()
            source = doc.get("source","")
            date = doc.get("date","")
            return f"{answer}\n\nSource: {source}\nLast updated from sources: {date}"

        # Priority 3: find any sentence with a numeric pattern (useful for AUM, NAV, etc.)
        sent3 = self._find_numeric_pattern_sentence(text)
        if sent3:
            answer = sent3.strip()
            source = doc.get("source","")
            date = doc.get("date","")
            return f"{answer}\n\nSource: {source}\nLast updated from sources: {date}"

        # Fallback: return first up-to-3 sentences from the doc text
        sents = self._split_sentences(text)
        if sents:
            ans = ' '.join(sents[:3]).strip()
            source = doc.get("source","")
            date = doc.get("date","")
            return f"{ans}\n\nSource: {source}\nLast updated from sources: {date}"

        return "I couldn't find a direct factual statement in the documents."

    def answer(self, query):
        if not query or not query.strip():
            return "Please ask a factual question about the covered schemes."
        results = self.retrieve(query, top_k=1)
        if not results:
            return "I couldn't find a factual answer in the available sources."
        doc, score = results[0]
        return self.format_answer(doc, query)
