# Predictive Maintenance ML Dashboard

An end-to-end predictive maintenance project that uses sensor time-series data to predict Remaining Useful Life (RUL), classify machine risk, and generate maintenance recommendations.

This project demonstrates applied ML engineering rather than notebook-only modelling. It includes a training pipeline, FastAPI backend, Streamlit dashboard, saved model artifact, and SQLite prediction history.

## Project Overview

Predictive maintenance means using data to estimate when equipment may need service before it fails. Instead of waiting for a breakdown, the system looks at sensor patterns and helps decide whether maintenance should happen soon.

Remaining Useful Life, or RUL, is the estimated number of operating cycles a machine has left before failure. A lower RUL means the machine is closer to needing maintenance.

Time-series sensor data matters because machines degrade over time. A single sensor reading may not say much, but trends across recent cycles can reveal changes in temperature, pressure, vibration, or other signals that point to wear.

This project predicts RUL and converts that number into a practical operational risk level:

- **High risk**
- **Medium risk**
- **Low risk**

The dashboard presents the prediction, sensor trends, recommendation text, model metadata, and recent prediction history.

## Dashboard Preview

![Dashboard Overview](screenshots/dashboard_overview.png)

Streamlit dashboard with sensor trend, prediction history, and model metadata.

![Prediction Result](screenshots/prediction_result.png)

Example RUL prediction, risk level, and maintenance recommendation.

![FastAPI Docs](screenshots/fastapi_docs.png)

FastAPI Swagger documentation showing `/health` and `/predict` endpoints.

## Architecture

```text
Streamlit Dashboard
        |
        | HTTP request: /predict
        v
FastAPI Backend
        |
        | feature engineering + model inference
        v
Saved ML Model
        |
        | prediction result
        v
SQLite Prediction History
```

In short:

```text
Streamlit -> FastAPI -> ML Model -> SQLite
```

The frontend and backend run as separate local services. Streamlit sends recent sensor readings to FastAPI, FastAPI loads the trained model, predicts RUL, saves the prediction to SQLite, and returns the result for display.

## How The System Works

### 1. Streamlit Dashboard

The dashboard is the user-facing part of the project. It lets a user select a machine, view sensor trends, request a prediction, and review previous predictions.

### 2. FastAPI Backend

FastAPI receives prediction requests from Streamlit. It validates the request, prepares the data for inference, calls the model, and returns a clean JSON response.

### 3. ML Model Inference

The trained model estimates RUL from engineered features created from recent sensor readings. The raw model output is then converted into a risk level and maintenance recommendation.

### 4. SQLite Prediction History

SQLite stores each successful prediction locally. This gives the dashboard a simple history view and makes it easier to inspect what the system predicted over time.

## Training vs Inference

Training and inference are intentionally separate.

`src/models/train.py` trains the model offline. It loads historical sensor data, creates RUL labels, builds features, trains the model, evaluates it, and saves the trained artifact to `models/`.

FastAPI does not retrain the model. During prediction, it only loads the saved model and uses it to make new predictions.

This separation matters because training can be slow and experimental, while inference should be fast, repeatable, and reliable for the dashboard.

## Why This Architecture?

The frontend and backend are decoupled so each part has a clear job. Streamlit focuses on the user experience, while FastAPI focuses on validation, prediction logic, and persistence.

The API design makes the model reusable. Another frontend, scheduled job, or external service could call `/predict` without changing the ML code.

FastAPI also helps with debugging because `/docs`, `/health`, and structured request validation make it easier to test the backend separately from the dashboard.

SQLite is enough for this local MVP because prediction history is small and runs on one machine. For a production system with many users or machines, PostgreSQL or another managed database would be a better fit.

## Technology Stack

- **Python**: core language
- **pandas / NumPy**: data loading and preprocessing
- **scikit-learn**: model training and persistence
- **FastAPI**: backend prediction API
- **Streamlit**: frontend dashboard
- **SQLite**: local prediction history
- **Plotly**: sensor trend visualization
- **pytest**: lightweight testing

## Local Setup

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Generate sample C-MAPSS-like data:

```powershell
py -m scripts.create_sample_data
```

Train the model:

```powershell
py -m scripts.train_model --data data/raw/sample_train_FD001.txt
```

Run the FastAPI backend:

```powershell
py -m uvicorn api.main:app --reload --port 8000
```

Run the Streamlit dashboard in a second terminal:

```powershell
py -m streamlit run app/dashboard.py
```

Open:

```text
FastAPI docs: http://127.0.0.1:8000/docs
Dashboard:    http://localhost:8501
```

Run tests:

```powershell
py -m pytest tests
```

## API Endpoints

### `GET /health`

Checks that the backend is running and reports whether the trained model artifact exists.

Example response:

```json
{
  "status": "ok",
  "model_available": true
}
```

### `POST /predict`

Accepts recent sensor cycles for a machine and returns the RUL prediction, risk level, and recommendation.

Example response:

```json
{
  "unit_id": 1,
  "predicted_rul": 7.46,
  "risk_level": "high",
  "recommendation": "Schedule immediate inspection. Predicted RUL is about 7 cycles, so defer non-critical operation until maintenance is reviewed."
}
```

### `GET /history`

Returns recent prediction records saved by the backend.

## Dashboard Features

- Select a machine/unit from the dataset
- View sensor trends across operating cycles
- View a focused latest-window sensor trend chart
- Send recent sensor readings to FastAPI for prediction
- Display predicted RUL, risk level, and recommendation
- Show the latest prediction history from SQLite
- Display model metadata after training

## Project Structure

```text
.
+-- api/                  # FastAPI backend
|   +-- main.py
|   +-- schemas.py
+-- app/                  # Streamlit frontend
|   +-- dashboard.py
+-- data/
|   +-- raw/              # raw or sample sensor data
|   +-- processed/        # optional processed data
|   +-- runtime/          # local SQLite database
+-- models/               # trained model artifacts
+-- scripts/              # data generation and training scripts
+-- src/
|   +-- data/             # data loading and RUL target creation
|   +-- database/         # SQLite helper functions
|   +-- features/         # feature engineering
|   +-- models/           # model training and loading
|   +-- services/         # prediction and recommendation logic
+-- tests/                # lightweight tests
+-- requirements.txt
+-- README.md
```

## Data Flow

1. Raw sensor time-series data is loaded from `data/raw/`.
2. The training pipeline creates the RUL target.
3. Feature engineering summarizes recent sensor windows.
4. The model is trained and saved to `models/`.
5. Streamlit sends selected recent cycles to FastAPI.
6. FastAPI builds inference features and predicts RUL.
7. The prediction is converted into risk and recommendation text.
8. FastAPI inserts the prediction record into SQLite.
9. Streamlit displays the prediction and recent history.

## Prediction History

The active local database is:

```text
data/runtime/predictions.db
```

The table is:

```text
prediction_history
```

Stored columns:

- `id`
- `unit_id`
- `predicted_rul`
- `risk_level`
- `recommendation`
- `created_at`

FastAPI inserts a new row after each successful `/predict` request.

## Example Workflow

1. Generate sample data.
2. Train the RUL model.
3. Start FastAPI on port `8000`.
4. Start the Streamlit dashboard.
5. Select a machine unit.
6. Review sensor trend charts.
7. Click **Predict Failure Risk**.
8. Review predicted RUL, risk level, recommendation, and prediction history.

## Key Engineering Concepts Learned

- **API validation**: FastAPI and Pydantic define the expected prediction request shape.
- **Model serving**: the trained model is loaded by the backend and used through an API.
- **Time-series preprocessing**: recent sensor windows are converted into useful model features.
- **Frontend/backend separation**: Streamlit handles interaction, while FastAPI handles prediction logic.
- **Persistence layer**: SQLite stores prediction history so results are not lost after one request.
- **Model metadata**: training metrics and model details are saved for transparency.
- **Training vs inference**: model training happens offline, while the API performs fast prediction only.

## Common Real-World Challenges

- **Model drift**: machines, environments, and sensor behavior can change over time, so model performance needs monitoring.
- **Bad input data**: missing sensors, noisy readings, or incorrect units can lead to unreliable predictions.
- **Preprocessing mismatches**: training and inference must use the same feature logic, or predictions may be misleading.
- **Scaling beyond SQLite**: SQLite is fine locally, but larger deployments usually need PostgreSQL or another production database.
- **Silent ML failures**: a model can return a number even when the input data is poor, so validation and monitoring are important.

## Current Limitations

- The included sample data is synthetic and mainly supports local demonstration.
- The model is a simple Random Forest regressor.
- Validation should be improved with machine-level train/test splits.
- SQLite is appropriate for local development, but not for high-concurrency production use.
- The dashboard expects the FastAPI backend to be running locally.
- The project does not currently include Docker, CI/CD, authentication, monitoring, or cloud deployment.

## Future Improvements

- Train and evaluate on the full NASA C-MAPSS dataset.
- Add better validation by splitting train/test data by machine unit.
- Compare additional models such as Gradient Boosting, XGBoost, LSTM, or temporal CNNs.
- Add model explainability with feature importance or SHAP.
- Add Docker and `docker-compose`.
- Add more tests for feature engineering, API prediction, and database writes.
- Add model versioning and experiment tracking.
- Add a short demo GIF for the GitHub README.

## What I Learned

This project helped me practice building an applied ML system beyond a notebook:

- converting time-series sensor data into model features
- training and saving an ML model
- serving predictions through FastAPI
- building a dashboard with Streamlit
- storing prediction history for traceability
- communicating predictions as practical maintenance actions

This is a portfolio project, not a production maintenance platform. The goal is to show clear ML engineering thinking in a runnable local system.
