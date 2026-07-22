from app.retrieval import BM25Retriever
from app.store import load_rules

def test_deadline_retrieval():
    retriever = BM25Retriever(load_rules())
    top = retriever.search("Welche Frist gilt für den Verwendungsnachweis?", limit=1)
    assert top
    assert top[0][0]["id"] == "bnbest_verwendungsnachweis_frist"

def test_photo_retrieval():
    retriever = BM25Retriever(load_rules())
    top = retriever.search("Was muss die Fotodokumentation enthalten?", limit=1)
    assert top[0][0]["id"] == "bnbest_photo_documentation"
