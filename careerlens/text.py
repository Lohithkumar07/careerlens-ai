"""Text normalisation shared by training and inference.

The exact same `features()` function is used when training the scikit-learn
model and when serving predictions, which guarantees train/serve parity.
"""
import re

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#.]*")

STOPWORDS = frozenset(
    """a an and are as at be by for from has have in into is it its of on or that
    the their this to was were will with we our you your i my me using used use
    also over per via within across including etc""".split()
)


def tokenize(text: str) -> list:
    """Lowercase, keep tech tokens like c++, c#, node.js; drop stopwords."""
    tokens = []
    for raw in _TOKEN_RE.findall(text.lower()):
        tok = raw.rstrip(".")
        if len(tok) < 2 and tok not in {"r"}:
            continue
        if tok in STOPWORDS or tok.isdigit():
            continue
        tokens.append(tok)
    return tokens


def features(text: str) -> list:
    """Unigrams + bigrams."""
    toks = tokenize(text)
    bigrams = [f"{a} {b}" for a, b in zip(toks, toks[1:])]
    return toks + bigrams
