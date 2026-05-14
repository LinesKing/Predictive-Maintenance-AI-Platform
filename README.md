# Predictive Maintenance ML Dashboard

## 1. Project Overview

This is an end-to-end predictive maintenance machine learning system built in Python. It uses machine sensor time-series data to predict Remaining Useful Life (RUL), then converts that prediction into a practical maintenance risk level and recommendation.

The goal is to demonstrate applied ML engineering: data loading, feature engineering, model training, model persistence, API serving, dashboarding, and prediction history storage. This is intentionally more than a notebook-only modelling project.

## 2. Why I Built This Project

Predictive maintenance is a common industrial AI use case where machine learning can support real operational decisions. I built this project to show how an ML model can be integrated into a small but complete software system.

The project is designed for portfolio and interview discussions around:

- turning sensor data into useful features
- training and saving an ML model
- serving predictions through an API
- building a simple dashboard for decision-making
- storing prediction history for traceability

## 3. System Architecture

```text
Sensor Time-Series Data
        |
        v
Data Loading + RUL Target Creation
        |
        v
Feature Engineering
        |
        v
ML Training Pipeline
        |
        v
Saved Model Artifact
        |
        v
FastAPI Prediction Service
        |
        +-----------------> SQLite Prediction History
        |
        v
Streamlit Dashboard
```

Main components:

- **Streamlit frontend**: visualizes sensor trends and displays predictions
- **FastAPI backend**: exposes `/health`, `/predict`, and `/history`
- **ML pipeline**: loads data, creates features, trains a model, saves artifacts
- **SQLite database**: stores prediction history

## 4. Data Flow

1. Raw sensor time-series data is loaded from `data/raw/`.
2. The training pipeline calculates Remaining Useful Life for each machine cycle.
3. Recent sensor readings are converted into tabular features such as latest value, mean, standard deviation, min, max, and trend.
4. A regression model predicts RUL.
5. The predicted RUL is converted into a risk level:
   - **High**
   - **Medium**
   - **Low**
6. The system generates a maintenance recommendation.
7. The API saves each prediction to SQLite.
8. The Streamlit dashboard displays trends, predictions, recommendations, and history.

## 5. Tech Stack

- **Python**: main programming language
- **pandas / NumPy**: data loading and manipulation
- **scikit-learn**: ML training and model persistence
- **FastAPI**: backend prediction API
- **Streamlit**: interactive dashboard
- **SQLite**: local prediction history database
- **Plotly**: sensor trend visualization
- **pytest**: lightweight tests

## 6. How To Run Locally

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
py -m uvicorn api.main:app --reload --port 8010
```

Open the API docs:

```text
http://127.0.0.1:8010/docs
```

Run the Streamlit frontend in a second terminal:

```powershell
py -m streamlit run app/dashboard.py
```

Open the dashboard:

```text
http://127.0.0.1:8501
```

Run tests:

```powershell
py -m pytest tests
```

## 7. What Each Component Does

`scripts/create_sample_data.py`  
Creates sample turbofan-style sensor data so the project can run locally without immediately downloading a large dataset.

`scripts/train_model.py`  
Runs the model training pipeline from the command line.

`src/data/cmapss.py`  
Loads C-MAPSS-style data and creates the RUL training target.

`src/features/build_features.py`  
Converts recent sensor time-series windows into model-ready features.

`src/models/train.py`  
Trains the RUL regression model, evaluates it, and saves the trained artifact.

`src/services/predictor.py`  
Loads the saved model and runs inference for new sensor readings.

`src/services/recommendations.py`  
Converts predicted RUL into high, medium, or low risk and creates maintenance recommendation text.

`src/database/db.py`  
Initializes SQLite and stores prediction history.

`api/main.py`  
Provides the FastAPI backend endpoints.

`app/dashboard.py`  
Provides the Streamlit dashboard for visualization and prediction.

## 8. Example Workflow

1. Generate or download turbofan sensor data.
2. Train the RUL model.
3. Start the FastAPI backend.
4. Start the Streamlit dashboard.
5. Select a machine unit in the dashboard.
6. Review sensor trends over time.
7. Click the prediction button.
8. View predicted RUL, risk level, and recommendation.
9. Review stored prediction history.

Example output:

```text
Predicted RUL: 32.5 cycles
Risk level: Medium
Recommendation: Plan maintenance within the next service window.
```

## 9. Current Limitations

- The included sample data is synthetic and mainly supports local demonstration.
- The model is a simple Random Forest regressor, not a highly optimized industrial model.
- Validation is basic and should be improved with machine-level train/test splitting.
- The dashboard assumes the FastAPI backend is already running.
- SQLite is suitable for local development, but not ideal for high-concurrency production use.
- The project does not currently include Docker, CI/CD, authentication, monitoring, or cloud deployment.

## 10. Future Improvements

- Train and evaluate on the full NASA C-MAPSS dataset.
- Add unit-level train/test splitting to better measure generalization.
- Compare models such as Gradient Boosting, XGBoost, LSTM, or temporal CNNs.
- Add model explainability using feature importance or SHAP.
- Add Docker and `docker-compose` for easier deployment.
- Add more tests for feature engineering, API prediction, and database writes.
- Add model versioning and experiment tracking.
- Improve dashboard UX with fleet-level summaries and alert filtering.

## 11. What I Learned

This project helped me practice building an applied ML system beyond notebook modelling. Key learnings included:

- designing a simple ML system with clear service boundaries
- converting time-series sensor data into regression features
- persisting and reusing trained model artifacts
- exposing ML predictions through FastAPI
- building a dashboard that supports operational decisions
- storing prediction history for traceability
- communicating model output as risk levels and recommendations

The project is not presented as a fully production-grade system. It is a practical portfolio project that demonstrates the engineering steps needed to turn an ML model into a usable application.
