from careerlens.service import handle_analyze, health

RESUME = ("Final year student. Skills: Python, pandas, numpy, scikit-learn, SQL, matplotlib, statistics. "
          "Experience: analyzed customer churn and built predictive models using pandas and scikit-learn.")
JD = "We need a data scientist with Python, SQL, machine learning, statistics, tableau and A/B testing experience."


def test_health():
    assert health()["status"] == "ok"


def test_analyze_basic():
    status, body = handle_analyze({"resume": RESUME})
    assert status == 200
    assert body["top_role"] in {"Data Scientist", "Data Analyst"}
    assert body["match"] is None
    assert any(s["name"] == "python" for s in body["skills"])


def test_analyze_with_job_description():
    status, body = handle_analyze({"resume": RESUME, "job_description": JD})
    assert status == 200
    m = body["match"]
    assert 0 <= m["score"] <= 100
    assert "tableau" in m["missing_skills"] and "python" in m["matched_skills"]


def test_analyze_with_target_role():
    status, body = handle_analyze({"resume": RESUME, "target_role": "Data Scientist"})
    assert status == 200 and body["match"]["source"] == "Data Scientist profile"


def test_validation_errors():
    assert handle_analyze([])[0] == 400
    assert handle_analyze({"resume": "short"})[0] == 400
    assert handle_analyze({"resume": 5})[0] == 400
    assert handle_analyze({"resume": "x" * 30_001})[0] == 413
    assert handle_analyze({"resume": RESUME, "target_role": "Wizard"})[0] == 422
    assert handle_analyze({"resume": "I enjoy long walks on the beach and quiet evenings at home."})[0] == 422
