# CareerLens

Resume analyzer that predicts which roles a resume points to, extracts skills, and scores the match against a job description, showing exactly which required skills are missing.

- **Model:** TF-IDF (unigrams + bigrams, sublinear tf) + multinomial logistic regression, 12 roles
- **Explainable:** every prediction returns the terms that pushed it toward the top role
- **Fast to deploy:** trained with scikit-learn, exported to JSON, served by **pure-Python inference** (no numpy or scikit-learn at runtime), so Vercel cold starts stay small
- **Tested:** 15 pytest tests including a parity check against scikit-learn's own probabilities, run in GitHub Actions

## Project layout

```
api/            Vercel serverless functions (analyze.py, health.py)
careerlens/     inference package: text, skills, model, matcher, service
  data/         model.json (exported weights) and metrics.json
public/         static frontend (index.html)
training/       synthetic data generator and training script
tests/          pytest suite
dev_server.py   local server that mimics Vercel
```

## Run locally

```bash
python dev_server.py          # http://localhost:8000, no installs needed
```

To retrain or run tests:

```bash
pip install -r requirements-dev.txt
python -m training.train      # rewrites careerlens/data/model.json
pytest -q
```

## Deploy

1. Push to GitHub:
   ```bash
   git init && git add . && git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<you>/careerlens-ai.git
   git push -u origin main
   ```
2. In Vercel choose **Add New → Project**, import the repo, and keep the defaults (Framework Preset: **Other**, no build command, no output directory). Click **Deploy**.

Or with the CLI: `npm i -g vercel && vercel --prod`.

## API

`POST /api/analyze`

```json
{ "resume": "…", "job_description": "… (optional)", "target_role": "Data Scientist (optional)" }
```

Returns `predicted_roles`, `top_role`, `skills`, `key_terms`, and `match` (`score`, `matched_skills`, `missing_skills`). `GET /api/health` returns model info and the list of target roles.

```bash
curl -X POST https://<your-app>.vercel.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"resume":"Python, pandas, scikit-learn, SQL, statistics. Built churn models.","target_role":"Data Scientist"}'
```

## Important: the training data is synthetic

Real labelled resumes are private, so `training/generate_data.py` builds resumes from role skill profiles (with overlapping roles and 3% label noise). The reported ~97% accuracy therefore measures how well the model learned those profiles, not real-world hiring accuracy. To use real data, replace `build_dataset()` with a loader for your own labelled resumes and rerun `python -m training.train`.

## Ideas to extend

- Replace TF-IDF with sentence embeddings (needs a larger runtime or a separate inference service)
- PDF upload with server-side text extraction
- Calibrate probabilities and add a "not enough information" threshold
- Add more roles by editing `ROLE_PROFILES` in `careerlens/skills.py`

## License

MIT
