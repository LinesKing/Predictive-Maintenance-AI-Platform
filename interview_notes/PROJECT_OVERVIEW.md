# Project Overview

## One-Sentence Explanation

Predictive Maintenance AI Platform is an end-to-end machine learning demo that predicts Remaining Useful Life (RUL) from machine sensor data, classifies operational risk, and presents maintenance guidance in an industrial monitoring dashboard.

## Problem Solved

Industrial equipment can fail unexpectedly, causing downtime, safety risk, and expensive emergency maintenance. This project demonstrates how recent sensor readings can be converted into useful operational signals:

- predicted remaining useful life
- risk level
- maintenance recommendation
- machine health dashboard view

The goal is not to replace a real maintenance engineer. The goal is to show how an ML system can turn sensor data into an actionable decision-support workflow.

## Target Users

- Maintenance engineers who need early warning about machine degradation.
- Operations managers who need a fleet-level view of asset health.
- Reliability engineers who want to prioritize inspection and service windows.
- Data/ML teams who need a prototype pattern for serving predictive maintenance models.

## Business And Operational Value

The business value is reducing unplanned downtime and helping teams schedule maintenance before failures happen.

Operationally, the project shows how AI can support:

- earlier risk detection
- better maintenance prioritization
- clearer communication of model output
- local prediction history
- dashboard-based monitoring

## What I Should Understand For Interviews

I should explain this as a portfolio-grade engineering project, not as a finished production system.

Strong explanation:

> I built a predictive maintenance platform that takes recent machine sensor cycles, engineers time-window features, predicts Remaining Useful Life with a scikit-learn regression model, converts the prediction into risk levels, and displays the result in a Streamlit monitoring dashboard. Locally it can use a FastAPI backend, while the deployed Streamlit version uses direct model inference because Streamlit Community Cloud does not host the FastAPI service.

## Demo-Level vs Production-Level

Demo-level:

- Synthetic/sample C-MAPSS-style data is used.
- The model is a simple Random Forest baseline.
- SQLite is used for local prediction history.
- Risk thresholds are rule-based.
- Streamlit Cloud deployment uses direct model inference instead of a separately hosted API.

Production-level patterns demonstrated:

- separated training, inference, API, dashboard, and service logic
- reusable predictor class
- API request/response schemas
- model artifact and metadata persistence
- environment-based prediction modes
- test coverage for important business rules
- deployment-specific fallback handling

## How I Would Improve This In Production

- Train and validate on the full NASA C-MAPSS dataset or real sensor data.
- Use machine-level train/test splits to avoid leakage across equipment behavior.
- Add drift monitoring and data quality checks.
- Add model versioning and experiment tracking.
- Host FastAPI separately for production inference.
- Replace SQLite with PostgreSQL or another managed database.
- Add authentication, API rate limits, and audit logs.
- Add explainability for maintenance engineers, such as feature importance or SHAP.
- Add CI/CD so tests run automatically before deployment.
