# Sixty Second Pitch

## 30-Second Version

I built a Predictive Maintenance AI Platform that predicts machine Remaining Useful Life from sensor data and turns the prediction into risk levels and maintenance recommendations. It includes a Streamlit monitoring dashboard, a FastAPI backend for local model serving, and a direct model mode for Streamlit Cloud deployment. The focus was building an end-to-end ML engineering project, not just training a model in a notebook.

## 60-Second Version

This project is an end-to-end predictive maintenance platform. It uses C-MAPSS-style machine sensor data to train a regression model that predicts Remaining Useful Life. I engineered rolling-window features from recent sensor cycles, trained a scikit-learn Random Forest model, and wrapped inference in a shared predictor service.

Locally, the dashboard can call a FastAPI backend, which validates requests, serves predictions, and stores prediction history in SQLite. For deployment on Streamlit Cloud, I added a direct prediction mode where Streamlit loads the model artifact directly, because the free Streamlit deployment does not host a separate FastAPI service.

The dashboard presents system health, sensor trends, predicted RUL, risk level, and maintenance recommendations. It is honest demo-level work, but it uses production-style patterns like separated services, reusable inference logic, environment-based configuration, tests, and clear deployment documentation.

## 2-Minute Technical Version

I built a predictive maintenance ML platform to demonstrate how sensor data can be turned into operational maintenance decisions.

The data is C-MAPSS-style machine sensor data. For each machine unit, I calculate Remaining Useful Life as the difference between the unit's final cycle and the current cycle. Then I convert recent time windows into tabular features. For each sensor, I calculate latest value, mean, standard deviation, min, max, and trend. This gives the model both current machine state and short-term degradation behavior.

The model is a scikit-learn pipeline with a scaler and Random Forest Regressor. I chose that as a strong baseline because it is explainable, fast to train, and easy to serve. The saved artifact includes the pipeline, feature columns, and window size, and I also write metadata such as MAE, RMSE, feature count, and training timestamp.

For inference, I created a shared `MaintenancePredictor` service. It builds inference features, aligns them with the training feature columns, predicts RUL, clamps negative values to zero, maps the result into `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`, and returns a maintenance recommendation.

The project has two serving modes. In local API mode, Streamlit calls FastAPI. FastAPI validates the request with Pydantic, calls the predictor, stores prediction history in SQLite, and returns the response. In direct mode, Streamlit calls the same predictor service directly. I added direct mode because Streamlit Community Cloud hosts the dashboard but not a separate FastAPI backend.

The dashboard is designed as an industrial monitoring UI, with health cards, risk score, risk badge, sensor trend chart, latest sensor window, model metadata, and a maintenance recommendation panel.

I would not describe it as production-ready. The data is demo-level, the model is a baseline, risk thresholds are rule-based, and SQLite is local. To productionize it, I would use real sensor data, better validation splits, model monitoring, a separately hosted API, managed database, authentication, model registry, and calibrated risk thresholds.

## CV Bullet Points

- Built an end-to-end predictive maintenance AI platform using Python, scikit-learn, FastAPI, Streamlit, Plotly, and SQLite.
- Engineered time-window sensor features to predict machine Remaining Useful Life from C-MAPSS-style data.
- Designed a shared model inference service used by both FastAPI API mode and Streamlit direct deployment mode.
- Implemented risk classification and maintenance recommendations from model predictions.
- Built an industrial monitoring dashboard with system health cards, sensor trends, risk score, prediction output, and model metadata.
- Deployed the project on Streamlit Community Cloud using direct model inference and environment-based configuration.

## LinkedIn Project Description

I deployed a Predictive Maintenance AI Platform that predicts machine Remaining Useful Life from sensor data and translates model output into operational risk levels and maintenance recommendations.

The project includes a scikit-learn regression model, time-window feature engineering, FastAPI inference API for local development, Streamlit monitoring dashboard, SQLite prediction history, and a Streamlit Cloud deployment using direct model inference.

The main engineering focus was turning an ML model into a usable system: reproducible training, model artifact persistence, API validation, shared inference logic, deployment-specific configuration, and a dashboard that communicates actionable maintenance decisions.

This is a portfolio project rather than a production maintenance system, but it demonstrates the type of end-to-end ML engineering workflow I want to build on: data processing, model serving, UI integration, deployment, testing, and clear documentation.

## How I Would Improve This In Production

- Use real maintenance records and failure labels.
- Validate by machine unit or time-based splits.
- Compare multiple model families and track experiments.
- Add explainability and uncertainty estimates.
- Deploy FastAPI as a separate production service.
- Replace SQLite with PostgreSQL.
- Add authentication, monitoring, CI/CD, and model versioning.
- Calibrate risk thresholds with maintenance cost and operational constraints.
