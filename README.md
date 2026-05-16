# Predictive Maintenance ML Dashboard

An end-to-end predictive maintenance project that uses sensor time-series data to predict Remaining Useful Life (RUL), classify machine risk, and generate maintenance recommendations.

This project is designed to demonstrate applied ML engineering rather than notebook-only modelling. It includes a training pipeline, FastAPI backend, Streamlit dashboard, saved model artifact, and SQLite prediction history.

## Project Overview

The system predicts how many cycles a machine may have left before failure. The prediction is converted into a simple operational risk level:

- **High risk**
- **Medium risk**
- **Low risk**

The dashboard then presents the prediction, sensor trends, recommendation text, and recent prediction history.

## Architecture Diagram

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

## Technology Stack

- **Python**: core language
- **pandas / NumPy**: data loading and preprocessing
- **scikit-learn**: model training and persistence
- **FastAPI**: backend prediction API
- **Streamlit**: frontend dashboard
- **SQLite**: local prediction history
- **Plotly**: sensor trend visualization
- **pytest**: lightweight testing

## Folder Structure

```text
.
├── api/                  # FastAPI backend
│   ├── main.py
│   └── schemas.py
├── app/                  # Streamlit frontend
│   └── dashboard.py
├── data/
│   ├── raw/              # raw or sample sensor data
│   ├── processed/        # optional processed data
│   └── runtime/          # local SQLite database
├── models/               # trained model artifacts
├── scripts/              # data generation and training scripts
├── src/
│   ├── data/             # data loading and RUL target creation
│   ├── database/         # SQLite helper functions
│   ├── features/         # feature engineering
│   ├── models/           # model training and loading
│   └── services/         # prediction and recommendation logic
├── tests/                # lightweight tests
├── requirements.txt
└── README.md
```

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

## Screenshots

Add screenshots here before publishing the repository:

```text
screenshots/dashboard-overview.png
screenshots/prediction-result.png
screenshots/prediction-history.png
```

Suggested screenshots:

- Dashboard overview with sensor trend chart
- Prediction result showing RUL and risk level
- Prediction history table
- FastAPI `/docs` page

## Example Workflow

1. Generate sample data.
2. Train the RUL model.
3. Start FastAPI on port `8000`.
4. Start the Streamlit dashboard.
5. Select a machine unit.
6. Review sensor trend charts.
7. Click **Predict Failure Risk**.
8. Review predicted RUL, risk level, recommendation, and prediction history.

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
- Add screenshots and a short demo GIF for the GitHub README.

## What I Learned

This project helped me practice building an applied ML system beyond a notebook:

- converting time-series sensor data into model features
- training and saving an ML model
- serving predictions through FastAPI
- building a dashboard with Streamlit
- storing prediction history for traceability
- communicating predictions as practical maintenance actions

This is a portfolio project, not a production maintenance platform. The goal is to show clear ML engineering thinking in a runnable local system.
