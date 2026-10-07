"""Resume analysis: role prediction, skill extraction, job-description matching."""
from .model import CareerModel
from .skills import ROLE_PROFILES, category_of, extract_skills


def _grade(score: int) -> str:
    if score >= 80:
        return "Strong match"
    if score >= 60:
        return "Good match"
    if score >= 40:
        return "Partial match"
    return "Weak match"


def analyze(model: CareerModel, resume: str, job_description: str = "", target_role: str = "", top_k: int = 5) -> dict:
    vec = model.vectorize(resume)
    ranked = model.predict_proba(resume, vec=vec)
    if not ranked:
        raise ValueError("The resume has no recognizable technical content. Add skills or project details.")

    resume_skills = extract_skills(resume)
    top_role = ranked[0][0]

    result = {
        "predicted_roles": [{"role": r, "probability": round(p, 4)} for r, p in ranked[:top_k]],
        "top_role": top_role,
        "skills": [{"name": s, "category": category_of(s)} for s in resume_skills],
        "key_terms": [{"term": t, "weight": w} for t, w in model.explain(resume, top_role, vec=vec)],
        "match": None,
    }

    required, source = [], None
    if job_description.strip():
        required, source = extract_skills(job_description), "job description"
    elif target_role:
        if target_role not in ROLE_PROFILES:
            raise ValueError(f"Unknown target role: {target_role}")
        required, source = sorted(ROLE_PROFILES[target_role]), f"{target_role} profile"

    if required:
        have = sorted(set(required) & set(resume_skills))
        missing = sorted(set(required) - set(resume_skills))
        coverage = len(have) / len(required)
        if job_description.strip():
            similarity = model.cosine(vec, model.vectorize(job_description))
            score = round(100 * (0.7 * coverage + 0.3 * min(1.0, similarity * 2)))
        else:
            score = round(100 * coverage)
        result["match"] = {
            "score": score,
            "grade": _grade(score),
            "source": source,
            "matched_skills": have,
            "missing_skills": missing,
            "coverage": round(coverage, 4),
        }
    elif job_description.strip():
        result["match"] = {
            "score": None, "grade": "No known skills found in the job description",
            "source": "job description", "matched_skills": [], "missing_skills": [], "coverage": 0,
        }
    return result
