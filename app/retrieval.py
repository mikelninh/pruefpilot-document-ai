from __future__ import annotations

from collections import Counter
import math
import re

TOKEN_RE = re.compile(r"[A-Za-zÄÖÜäöüß0-9]+")
STOPWORDS = {
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer", "einem", "einen",
    "und", "oder", "ist", "sind", "wird", "werden", "zu", "zur", "zum", "im", "in", "auf",
    "mit", "für", "von", "nach", "bei", "als", "wie", "was", "welche", "welcher", "muss",
    "müssen", "ich", "wir", "es", "wann", "gilt", "gelten",
}


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
        if token.lower() not in STOPWORDS and len(token) > 1
    ]


class BM25Retriever:
    def __init__(self, documents: list[dict], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.tokens = [
            tokenize(" ".join([doc.get("title", ""), doc.get("text", ""), " ".join(doc.get("tags", []))]))
            for doc in documents
        ]
        self.lengths = [len(tokens) for tokens in self.tokens]
        self.avgdl = sum(self.lengths) / max(len(self.lengths), 1)
        self.df = Counter()
        for tokens in self.tokens:
            self.df.update(set(tokens))

    def _idf(self, token: str) -> float:
        n = len(self.documents)
        df = self.df.get(token, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def search(self, query: str, limit: int = 4) -> list[tuple[dict, float]]:
        q = tokenize(query)
        scored: list[tuple[dict, float]] = []
        for doc, tokens, dl in zip(self.documents, self.tokens, self.lengths):
            tf = Counter(tokens)
            score = 0.0
            for token in q:
                freq = tf.get(token, 0)
                if not freq:
                    continue
                denom = freq + self.k1 * (1 - self.b + self.b * dl / max(self.avgdl, 1))
                score += self._idf(token) * (freq * (self.k1 + 1)) / denom
            title_tokens = set(tokenize(doc.get("title", "")))
            tag_tokens = set(tokenize(" ".join(doc.get("tags", []))))
            for token in q:
                if token in title_tokens:
                    score += 0.28
                if token in tag_tokens:
                    score += 0.16
            if score > 0:
                scored.append((doc, round(score, 4)))
        return sorted(scored, key=lambda item: item[1], reverse=True)[:limit]
