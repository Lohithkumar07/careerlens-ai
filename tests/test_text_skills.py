from careerlens.skills import extract_skills
from careerlens.text import features, tokenize


def test_tokenize_keeps_tech_tokens():
    toks = tokenize("Built APIs in C++ and C#, Node.js. Used the R programming language.")
    assert "c++" in toks and "c#" in toks and "node.js" in toks
    assert "the" not in toks


def test_features_include_bigrams():
    assert "machine learning" in features("machine learning models")


def test_extract_skills_aliases_and_boundaries():
    skills = extract_skills("Experienced with JavaScript, sklearn, K8s and PostgreSQL")
    assert {"javascript", "scikit-learn", "kubernetes", "postgresql"} <= set(skills)
    assert "java" not in skills  # 'java' must not match inside 'javascript'


def test_extract_skills_empty():
    assert extract_skills("I like hiking and cooking") == []
