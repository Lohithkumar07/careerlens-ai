"""Pure-Python inference for the exported TF-IDF + multinomial logistic regression model.

No numpy / scikit-learn at runtime: the Vercel function stays tiny and cold starts fast.
"""
import json
import math
from collections import Counter
from pathlib import Path

from .text import features

MODEL_PATH = Path(__file__).parent / "data" / "model.json"


class CareerModel:
    def __init__(self, path=MODEL_PATH):
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.classes = data["classes"]
        self.terms = data["terms"]
        self.index = {t: i for i, t in enumerate(self.terms)}
        self.idf = data["idf"]
        self.coef = data["coef"]
        self.intercept = data["intercept"]

    # ---- vectorisation (mirrors sklearn TfidfVectorizer(sublinear_tf=True, norm="l2"))
    def vectorize(self, text: str) -> dict:
        counts = Counter(f for f in features(text) if f in self.index)
        vec = {self.index[t]: (1.0 + math.log(c)) * self.idf[self.index[t]] for t, c in counts.items()}
        norm = math.sqrt(sum(v * v for v in vec.values()))
        if norm == 0:
            return {}
        return {i: v / norm for i, v in vec.items()}

    @staticmethod
    def cosine(a: dict, b: dict) -> float:
        if not a or not b:
            return 0.0
        if len(a) > len(b):
            a, b = b, a
        return sum(v * b.get(i, 0.0) for i, v in a.items())

    # ---- prediction
    def predict_proba(self, text: str, vec=None) -> list:
        vec = self.vectorize(text) if vec is None else vec
        if not vec:
            return []
        logits = [
            b + sum(w[i] * v for i, v in vec.items())
            for w, b in zip(self.coef, self.intercept)
        ]
        m = max(logits)
        exps = [math.exp(z - m) for z in logits]
        total = sum(exps)
        probs = sorted(zip(self.classes, (e / total for e in exps)), key=lambda x: -x[1])
        return [(c, p) for c, p in probs]

    def explain(self, text: str, role: str, top_k: int = 8, vec=None) -> list:
        """Terms in the text that push the prediction towards `role` (coef * tf-idf)."""
        vec = self.vectorize(text) if vec is None else vec
        row = self.coef[self.classes.index(role)]
        contrib = sorted(((self.terms[i], row[i] * v) for i, v in vec.items()), key=lambda x: -x[1])
        return [(t, round(c, 4)) for t, c in contrib[:top_k] if c > 0]
