# app.py - Streamlit frontend for SBI MF FAQ (replace your current file)
import streamlit as st
import json, os, traceback

st.set_page_config(page_title="SBI MF — Facts-only FAQ", layout="centered")
st.title("SBI Mutual Fund — Facts-only FAQ (INDMoney)")

st.markdown(
    "This is a facts-only assistant for SBI Mutual Fund schemes. "
    "Every answer cites exactly one official source. **No investment advice.**"
)

# show quick examples
st.info("Example questions:\n• What is the expense ratio of SBI Bluechip Fund?\n• Does SBI ELSS have a lock-in?\n• How do I download a capital-gains statement?")

# Load corpus safely
@st.cache_data(show_spinner=False)
def load_corpus(path="corpus.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)

corpus, corpus_err = load_corpus("corpus.json")
if corpus_err:
    st.error("Failed to load corpus.json: " + corpus_err)
    st.write("Files in repo root:")
    for f in sorted(os.listdir(".")):
        st.write("-", f)
    st.stop()

# Try importing RAGEngine from rag_engine.py
try:
    from rag_engine import RAGEngine
    engine = RAGEngine(corpus)
except Exception as e:
    # If rag_engine import fails, create a tiny fallback retriever
    st.warning("Warning: rag_engine import failed — using fallback retriever. Error:\n" + str(e))
    class SimpleFallback:
        def __init__(self, corpus):
            self.corpus = corpus
        def answer(self, query):
            q = query.lower()
            # return first doc that contains any word
            for d in self.corpus:
                if any(tok for tok in q.split() if tok and tok in d.get("text","").lower()):
                    fact = d.get("text","").split(".")[0]
                    return f"{fact}.\n\nSource: {d.get('source','')}\nLast updated from sources: {d.get('date','')}"
            d = self.corpus[0]
            fact = d.get("text","").split(".")[0]
            return f"{fact}.\n\nSource: {d.get('source','')}\nLast updated from sources: {d.get('date','')}"
    engine = SimpleFallback(corpus)

# Input
query = st.text_input("Ask a factual question about these schemes (type examples above):")

def looks_like_advice(q: str) -> bool:
    ql = q.lower()
    advice_triggers = ["should i", "should we", "which fund is better", "recommend", "advice", "buy", "sell"]
    return any(tok in ql for tok in advice_triggers)

if query:
    if looks_like_advice(query):
        st.warning("I provide facts only, not investment advice. For investor education visit: https://www.amfiindia.com/investor")
    else:
        try:
            answer = engine.answer(query)
            # ensure answer <= 3 sentences (very small trim)
            # but don't over-edit; show as returned
            st.markdown(answer.replace("\n", "\n\n"))
        except Exception as e:
            st.error("Error while generating answer: " + str(e))
            st.text(traceback.format_exc())

st.markdown("---")
st.caption("Sources: See `sources.csv` in repo. Last updated from sources: 2025-11-17")
