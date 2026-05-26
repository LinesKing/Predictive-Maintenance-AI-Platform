# Interview Q&A

## 1. What does this project do?

It predicts Remaining Useful Life for machine assets from recent sensor data, maps the prediction into a risk level, and shows maintenance guidance in a Streamlit dashboard. It also has a FastAPI backend for local serving and a direct model mode for Streamlit Cloud deployment.

## 2. What problem were you trying to solve?

The problem is unplanned equipment failure. In industrial settings, downtime can be expensive and risky. This project shows how sensor data can support earlier maintenance decisions by predicting degradation before failure.

## 3. Who are the users?

The intended users are maintenance engineers, reliability engineers, and operations managers. The dashboard is designed to help them understand which machines are at higher risk and what action should be taken.

## 4. What is Remaining Useful Life?

Remaining Useful Life is an estimate of how many operating cycles are left before an asset reaches failure. In this project, the model predicts RUL from recent sensor behavior.

## 5. How is the training target created?

For each machine unit, I calculate the maximum cycle observed and subtract the current cycle:

```text
RUL = max_cycle_for_unit - current_cycle
```

That creates a supervised regression target from time-series machine history.

## 6. What model did you use and why?

I used a Random Forest Regressor inside a scikit-learn pipeline. It is a strong tabular baseline, trains quickly, works well with engineered window features, and is easy to explain. For production, I would compare it against gradient boosting, survival analysis, and sequence models.

## 7. How does feature engineering work?

The system takes the latest window of machine cycles and summarizes each sensor with latest value, mean, standard deviation, min, max, and trend. This turns time-series data into tabular features that a scikit-learn model can use.

## 8. Why not use an LSTM or Transformer?

For a portfolio project, I prioritized a complete end-to-end system over a complex model. A Random Forest with clear features is easier to debug, serve, and explain. In production or deeper research, I would test sequence models and compare them against this baseline.

## 9. Does this project use RAG?

No. This project does not use retrieval-augmented generation. The recommendation system is rule-based: it maps the predicted RUL to risk levels and maintenance guidance. That makes the behavior deterministic and easy to validate.

## 10. How are risk levels calculated?

Risk is mapped from predicted RUL:

```text
CRITICAL: RUL <= 10
HIGH:     RUL <= 30
MEDIUM:   RUL <= 80
LOW:      RUL > 80
```

The thresholds are simple and explainable. In production, I would calibrate them with failure costs, maintenance capacity, and historical outcomes.

## 11. What is the architecture?

The architecture has data loading, feature engineering, model training, a shared predictor service, FastAPI routes, and a Streamlit dashboard. The key decision is that both FastAPI and Streamlit direct mode call the same `MaintenancePredictor` service.

## 12. Why did you build both FastAPI and direct Streamlit modes?

FastAPI mode shows a realistic local serving architecture. Direct mode solves the deployment constraint of Streamlit Community Cloud, where I deployed only the Streamlit app. By sharing the predictor service, I avoided duplicating model logic.

## 13. What happens in local mode?

In local API mode, Streamlit calls FastAPI. FastAPI validates the request, calls the predictor, stores the prediction in SQLite, and returns the prediction response to the dashboard.

## 14. What happens in deployed mode?

In deployed direct mode, Streamlit loads the saved model artifact directly and calls the predictor service without FastAPI. This keeps the public demo simple and free to host.

## 15. What were the hardest deployment issues?

Two practical issues came up. First, Streamlit Cloud did not automatically resolve the repository root for imports, so `src` imports failed. I fixed that by adding the project root to `sys.path` before local imports. Second, empty placeholder model/data files counted as existing, so I added checks for file size and regenerated demo artifacts when needed.

## 16. How did you test the project?

I added focused tests for prediction mode parsing, risk threshold boundaries, recommendations, and sensor simulator payload shape. I also used smoke tests for FastAPI health and Streamlit direct-mode import. For a production system, I would add integration tests for the full API prediction route and model artifact loading.

## 17. What is stored in SQLite?

SQLite stores local prediction history from the FastAPI workflow: timestamp, unit ID, predicted RUL, risk level, and recommendation. It is useful for a demo but not suitable for high-concurrency production use.

## 18. What would you improve first?

I would improve validation and evaluation first. Specifically, I would use a larger dataset, split by machine unit or time, compare multiple models, and add better performance metrics. Then I would add CI/CD and host the API separately.

## 19. What makes this more than a notebook project?

It has a trained model artifact, reusable feature engineering, a shared prediction service, API endpoints, request validation, a dashboard, deployment configuration, tests, and documentation. The project demonstrates system thinking around model serving and user-facing AI output.

## 20. How would you explain the main tradeoff?

The main tradeoff is practicality versus production completeness. I chose a simple, explainable model and a free deployment setup so the full system can be demonstrated end to end. For production, I would invest more in data quality, model validation, monitoring, security, and scalable infrastructure.

## How I Would Improve This In Production

If asked directly, say:

> I would not claim this is production-ready. To productionize it, I would use real historical sensor data, validate by machine or time period, deploy the API separately, replace SQLite with a managed database, add authentication, add model monitoring and drift detection, version the model artifact, and calibrate risk thresholds with maintenance cost and reliability requirements.
