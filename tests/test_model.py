import json
import math

import pytest

from careerlens.model import CareerModel
from careerlens.service import get_model
from training.generate_data import build_dataset


def test_probabilities_sum_to_one():
    probs = get_model().predict_proba("Python pytorch deep learning computer vision opencv")
    assert math.isclose(sum(p for _, p in probs), 1.0, rel_tol=1e-6)


def test_obvious_cases():
    m = get_model()
    assert m.predict_proba("Docker Kubernetes Terraform Ansible Prometheus Grafana CI/CD pipelines")[0][0] == "DevOps Engineer"
    assert m.predict_proba("Android Kotlin Flutter iOS Swift mobile apps published to app stores")[0][0] == "Mobile Developer"
    assert m.predict_proba("Tableau Power BI Excel SQL dashboards weekly reports")[0][0] == "Data Analyst"


def test_unknown_text_returns_empty():
    assert get_model().predict_proba("zzzz qqqq") == []


def test_generalises_to_fresh_synthetic_data():
    texts, labels = build_dataset(n_per_role=60, seed=2024, label_noise=0.0)
    m = get_model()
    correct = sum(m.predict_proba(t)[0][0] == y for t, y in zip(texts, labels))
    assert correct / len(texts) > 0.9


def test_explain_returns_positive_contributions():
    m = get_model()
    terms = m.explain("pytorch deep learning computer vision opencv", "Computer Vision Engineer")
    assert terms and all(w > 0 for _, w in terms)


def test_parity_with_sklearn():
    pytest.importorskip("sklearn")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    import numpy as np
    from careerlens.text import features

    texts, labels = build_dataset(n_per_role=40, seed=1)
    vec = TfidfVectorizer(analyzer=features, sublinear_tf=True, min_df=3, max_features=4000)
    X = vec.fit_transform(texts)
    clf = LogisticRegression(C=8.0, max_iter=3000).fit(X, labels)
    export = {
        "classes": list(clf.classes_),
        "terms": [t for t, _ in sorted(vec.vocabulary_.items(), key=lambda kv: kv[1])],
        "idf": vec.idf_.tolist(), "coef": clf.coef_.tolist(), "intercept": clf.intercept_.tolist(),
    }
    import tempfile, os
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(export, fh)
    try:
        mine = CareerModel(fh.name)
        for text in texts[:15]:
            ours = dict(mine.predict_proba(text))
            theirs = dict(zip(clf.classes_, clf.predict_proba(vec.transform([text]))[0]))
            for role in theirs:
                assert abs(ours[role] - theirs[role]) < 1e-6
    finally:
        os.unlink(fh.name)
