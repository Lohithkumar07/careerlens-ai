"""Transport-agnostic request handling, shared by Vercel functions and the dev server."""
from functools import lru_cache

from .matcher import analyze
from .model import CareerModel
from .skills import ROLE_PROFILES
from . import __version__

MAX_CHARS = 20_000


@lru_cache(maxsize=1)
def get_model() -> CareerModel:
    return CareerModel()


def health() -> dict:
    m = get_model()
    return {"status": "ok", "version": __version__, "roles": len(m.classes), "vocabulary": len(m.terms)}


def roles() -> list:
    return sorted(ROLE_PROFILES)


def handle_analyze(payload) -> tuple:
    """Return (http_status, json_body)."""
    if not isinstance(payload, dict):
        return 400, {"error": "Request body must be a JSON object."}
    resume = payload.get("resume", "")
    jd = payload.get("job_description", "") or ""
    target = payload.get("target_role", "") or ""
    if not all(isinstance(x, str) for x in (resume, jd, target)):
        return 400, {"error": "resume, job_description and target_role must be strings."}
    if len(resume.strip()) < 30:
        return 400, {"error": "Paste at least a few lines of your resume (30+ characters)."}
    if len(resume) > MAX_CHARS or len(jd) > MAX_CHARS:
        return 413, {"error": f"Text is too long. Limit is {MAX_CHARS:,} characters per field."}
    try:
        return 200, analyze(get_model(), resume, jd, target)
    except ValueError as exc:
        return 422, {"error": str(exc)}
