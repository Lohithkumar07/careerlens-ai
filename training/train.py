"""Train the role classifier and export it as portable JSON.

    pip install -r requirements-dev.txt
    python -m training.train
"""
import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline

from careerlens.text import features
from training.generate_data import build_dataset

OUT = Path(__file__).resolve().parent.parent / "careerlens" / "data"


def make_vectorizer():
    return TfidfVectorizer(analyzer=features, sublinear_tf=True, min_df=3, max_features=4000)


def make_classifier():
    return LogisticRegression(C=8.0, max_iter=3000)


def main():
    texts, labels = build_dataset()
    X_tr, X_te, y_tr, y_te = train_test_split(texts, labels, test_size=0.2, stratify=labels, random_state=7)

    # honest estimate: cross-validation on the training split, then one hold-out evaluation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)
    cv_scores = cross_val_score(make_pipeline(make_vectorizer(), make_classifier()), X_tr, y_tr, cv=cv, n_jobs=-1)

    vec, clf = make_vectorizer(), make_classifier()
    clf.fit(vec.fit_transform(X_tr), y_tr)
    pred = clf.predict(vec.transform(X_te))
    metrics = {
        "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
        "cv_accuracy_std": round(float(cv_scores.std()), 4),
        "holdout_accuracy": round(float(accuracy_score(y_te, pred)), 4),
        "holdout_macro_f1": round(float(f1_score(y_te, pred, average="macro")), 4),
        "train_size": len(X_tr), "test_size": len(X_te),
        "report": classification_report(y_te, pred, output_dict=True, zero_division=0),
        "data": "synthetic (see training/generate_data.py)",
    }
    print(classification_report(y_te, pred, zero_division=0))
    print(f"CV accuracy {metrics['cv_accuracy_mean']:.3f} ± {metrics['cv_accuracy_std']:.3f} | "
          f"hold-out {metrics['holdout_accuracy']:.3f}")

    # final model on all data
    vec, clf = make_vectorizer(), make_classifier()
    clf.fit(vec.fit_transform(texts), labels)
    terms = [t for t, _ in sorted(vec.vocabulary_.items(), key=lambda kv: kv[1])]
    model = {
        "classes": [str(c) for c in clf.classes_],
        "terms": terms,
        "idf": [round(float(x), 6) for x in vec.idf_],
        "coef": [[round(float(x), 5) for x in row] for row in clf.coef_],
        "intercept": [round(float(x), 6) for x in clf.intercept_],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "model.json").write_text(json.dumps(model, separators=(",", ":")), encoding="utf-8")
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    size_kb = (OUT / "model.json").stat().st_size / 1024
    print(f"Saved model.json ({size_kb:.0f} KB, {len(terms)} terms, {len(model['classes'])} roles)")


if __name__ == "__main__":
    main()
