# Industrial AI Platform Portfolio Playbook

Use this skill when turning an AI/ML demo into a production-style portfolio project with a Streamlit dashboard, optional FastAPI backend, model artifacts, reproducible local workflow, and cloud deployment path.

This playbook is based on the Predictive Maintenance AI Platform repository. It is intentionally practical: copy the patterns, avoid the pitfalls, and keep the project impressive without over-engineering it.

## Core Principle

Build a portfolio project like a small product, not a notebook export.

The final result should show:

- A clear business or operational problem.
- A trained model with reproducible training steps.
- A serving layer that can be tested independently.
- A dashboard that communicates decisions, not just charts.
- A README that helps recruiters, engineers, and beginners understand the system quickly.
- A deployment route that works within free hosting constraints.

## Recommended Architecture

Use a small layered architecture:

```text
.
+-- api/                  # FastAPI app, schemas, API-only persistence
+-- app/                  # Streamlit dashboard entrypoint
+-- data/
+   +-- raw/              # demo/raw data
+   +-- processed/        # generated feature outputs if needed
+   +-- runtime/          # SQLite and runtime-only local files
+-- models/               # model artifact and metadata
+-- scripts/              # CLI scripts for data generation and training
+-- src/
+   +-- config.py         # central paths and thresholds
+   +-- data/             # data loading and target creation
+   +-- features/         # reusable feature engineering
+   +-- models/           # train/load model helpers
+   +-- services/         # prediction, recommendations, simulation
+   +-- database/         # persistence helpers
+-- tests/                # focused behavior tests
+-- screenshots/          # README screenshots
```

Keep the core prediction logic out of both Streamlit and FastAPI. Put it in a service class such as `MaintenancePredictor`, then call that class from:

- FastAPI in local API mode.
- Streamlit in direct cloud mode.
- Tests and smoke checks.

This avoids duplicated inference logic and makes deployment mode a routing decision, not a model rewrite.

## Development Workflow

Start with a working baseline, then upgrade in small commits:

1. Inspect the repository structure and identify the existing frontend, backend, model, scripts, and tests.
2. Preserve the current runnable path before adding new features.
3. Add service-layer changes first, with tests.
4. Add API changes without breaking response field names.
5. Upgrade the dashboard while keeping the existing framework.
6. Polish README and deployment docs last.
7. Deploy only after local tests and direct-mode smoke checks pass.

Recommended local workflow:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py -m scripts.create_sample_data
py -m scripts.train_model --data data/raw/sample_train_FD001.txt
py -m pytest tests
```

For local API development:

```powershell
$env:PREDICTION_MODE="api"
py -m uvicorn api.main:app --reload --port 8000
```

In another terminal:

```powershell
$env:PREDICTION_MODE="api"
py -m streamlit run app/dashboard.py
```

## Prediction Mode Pattern

Use two prediction modes:

```text
PREDICTION_MODE=api
PREDICTION_MODE=direct
```

Default to `api` for local development because it demonstrates backend serving, validation, and persistence.

Use `direct` for Streamlit Cloud because only the Streamlit app is deployed. In direct mode, Streamlit loads the model artifact and calls the same predictor service used by FastAPI.

Use a small parser:

```python
VALID_PREDICTION_MODES = {"api", "direct"}

def normalize_prediction_mode(value: str | None) -> str:
    mode = (value or "api").strip().lower()
    if mode not in VALID_PREDICTION_MODES:
        raise ValueError(...)
    return mode
```

Read settings from both environment variables and Streamlit secrets:

```python
def get_app_setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default
```

Pitfall: `st.secrets.get(...)` can fail when no secrets file exists. Always catch exceptions and fall back.

## Streamlit Cloud Deployment Strategy

For free Streamlit Community Cloud, deploy only Streamlit:

```text
Repository: owner/repo
Branch: main
Main file path: app/dashboard.py
```

Set root-level Streamlit secret:

```toml
PREDICTION_MODE = "direct"
```

Do not deploy FastAPI unless using a separate backend host. Do not set API URLs, keys, or private secrets for direct mode.

Cloud app startup should tolerate missing artifacts:

- If demo data is missing or empty, generate it.
- If the model artifact is missing or empty, train a demo model once.
- Keep this fallback scoped to default demo paths, not arbitrary user paths.

Pitfall: an empty committed placeholder file still “exists.” Check both existence and file size:

```python
if not MODEL_PATH.exists() or MODEL_PATH.stat().st_size == 0:
    train_model(DEFAULT_DATA)
```

Pitfall: Streamlit Cloud may execute `app/dashboard.py` with `app/` as the import context. Add the repository root before local imports:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

## FastAPI Integration Pattern

Keep the API small and portfolio-readable:

- `GET /health`: return service status and model availability.
- `POST /predict`: validate input, call the predictor service, return model output plus risk and recommendation.
- `GET /history`: return recent SQLite prediction records if local persistence is part of the demo.

Keep response fields stable:

```json
{
  "unit_id": 1,
  "predicted_rul": 24.7,
  "risk_level": "HIGH",
  "recommendation": "..."
}
```

Use Pydantic schemas for API request/response validation. Convert validated cycles into a DataFrame only inside the API route.

Cache the predictor in FastAPI with `lru_cache(maxsize=1)` so the model is loaded once per process.

## Model Serving Pattern

Use a predictor service as the single inference boundary:

```text
raw recent cycles
  -> feature builder
  -> persisted model pipeline
  -> predicted value
  -> risk mapping
  -> recommendation text
```

Store model artifacts as:

- `models/rul_model.joblib`
- `models/model_metadata.json`

Metadata should include at least:

- training rows
- feature count
- window size
- metrics such as MAE/RMSE
- training timestamp
- data path

Risk translation should be simple, visible, and tested. Example:

```text
CRITICAL: RUL <= 10
HIGH:     RUL <= 30
MEDIUM:   RUL <= 80
LOW:      RUL > 80
```

Portfolio dashboards should not stop at raw prediction values. Convert model output into operational language:

- risk badge
- risk score
- maintenance recommendation
- health status
- trend context

## Streamlit UI/UX Conventions

Make the dashboard look like an operational monitoring tool, not a tutorial page.

Recommended first screen:

- Clear platform title.
- Four system health cards.
- Machine selector and controls in sidebar.
- Sensor trend chart.
- Risk score and prediction panel.
- Recommendation panel.
- Recent data window and model metadata.

For industrial AI dashboards:

- Use a dark, high-contrast theme.
- Use graphite card surfaces, restrained borders, and minimal accent color.
- Avoid excessive gradients and decorative elements.
- Make metric values large and readable.
- Use uppercase risk levels for fast scanning.
- Provide clear loading, empty, and error states.
- Keep labels practical: “Prediction Mode,” “Model,” “Direct Inference,” “Machine Fleet.”

Pitfall: custom CSS can fight Streamlit’s theme. Avoid white cards on a dark page unless all text colors are explicitly set. Style metric labels and values directly when using dark custom cards.

## Git Workflow With Codex

Use small safe commits:

```text
1. service/risk logic
2. simulator/tests
3. API health/predict compatibility
4. dashboard UI
5. README polish
6. deployment fixes
```

Before editing:

- Inspect files with `rg --files` and targeted reads.
- Summarize the file-change plan for the user.
- Keep unrelated user changes intact.

After editing:

- Run tests.
- Run direct/API smoke checks.
- Commit only intended files.
- Push after confirming local status.

On Windows, Git may exist through GitHub Desktop or SourceTree even when `git` is not on PATH. Search for bundled Git if needed. If files were changed through GitHub directly, verify local and remote commits before pulling or rebasing.

Recommended checks:

```powershell
git status --short --branch
git log --oneline -5 --decorate
git diff -- app/dashboard.py
```

Avoid rebasing when a fast-forward pull is enough. If local edits duplicate a remote fix, stash first, pull, inspect the stash, then drop only if it contains no unique work.

## Deployment Checklist

Before deploying:

- `py -m pytest tests` passes.
- Direct-mode smoke import succeeds.
- Default app entrypoint is correct, usually `app/dashboard.py`.
- `requirements.txt` includes Streamlit, pandas, scikit-learn, Plotly, requests, and any API dependencies used locally.
- `PREDICTION_MODE=direct` is set in Streamlit Cloud secrets.
- The app does not require FastAPI in cloud mode.
- The dashboard handles missing or empty demo data/model artifacts.
- Local package imports work when Streamlit runs a nested app file.
- No private keys, tokens, or `.env` files are committed.
- README explains both local API mode and cloud direct mode.
- Screenshots are present or placeholders are clearly labeled.

Useful smoke commands:

```powershell
$env:PREDICTION_MODE="direct"
py -c "import app.dashboard; print('direct import ok')"
```

```powershell
py -c "from fastapi.testclient import TestClient; from api.main import app; c=TestClient(app); print(c.get('/health').json())"
```

## README Structure

Use a recruiter-friendly README:

1. Project title and one-paragraph overview.
2. Why the project matters.
3. Architecture diagram in text or Mermaid.
4. Tech stack.
5. Features.
6. Project structure.
7. Local setup.
8. Local API workflow.
9. Streamlit Cloud direct deployment workflow.
10. Environment variables.
11. API examples.
12. Screenshots.
13. Testing.
14. Future improvements.
15. CV bullet points.
16. Current limitations.

Write it as an industrial AI platform, not a tutorial. Mention the real engineering decisions: serving mode, model artifact, health endpoint, persistence, and deployment constraints.

## Common Pitfalls And Fixes

- `ModuleNotFoundError: No module named 'src'` on Streamlit Cloud: add repo root to `sys.path` before local imports.
- App crashes when secrets are absent: wrap `st.secrets` access in `try/except`.
- Cloud direct mode tries to call FastAPI: ensure `PREDICTION_MODE=direct` is set in Streamlit secrets.
- Empty model/data artifacts exist but are unusable: check `stat().st_size == 0`.
- Dashboard cards look blank in dark mode: remove light card backgrounds or explicitly set text colors.
- Model logic duplicated between API and Streamlit: move inference into a service class and call it from both places.
- Deployment fails after GitHub-side edits: check local `HEAD`, `origin/main`, and `git status` before rebasing.
- Portfolio looks like a notebook demo: add health cards, risk translation, recommendations, README architecture, tests, and a cloud deployment path.

## Production-Style Portfolio Principles

- Keep scope small but complete.
- Prefer one strong end-to-end path over many unfinished features.
- Use realistic domain language.
- Show operational outputs, not only model metrics.
- Make failures visible and understandable.
- Keep the default local workflow reproducible.
- Make cloud deployment practical, even if simplified.
- Document limitations honestly.
- Add tests around business rules, mode parsing, payload shape, and model-serving boundaries.
- Preserve working functionality while upgrading in small increments.
