# PRANA Cardiovascular Digital Twin — ML POC

A small Python/VS Code prototype for classifying **synthetic baseline deviations** in hourly cardiovascular measurements.

## Safety and scope

- This project does **not** diagnose, predict, or prevent heart attacks.
- Synthetic labels and metrics are demonstration artifacts, not clinical evidence.
- A model's confidence is classification confidence, not probability of a medical event.
- Missing readings are represented by missingness indicators. Rows where all six measurements are missing are excluded from supervised training.
- A no-flag result must never be used to rule out an emergency or delay urgent care.
- Family notifications must only be sent after backend authorization/consent checks and the persistence rule.

## 1. Install Python

Use Python 3.11 or 3.12 if possible. During installation on Windows, select **Add Python to PATH**.

Open this folder in VS Code, then open Terminal → New Terminal.

Check:
```powershell
python --version
```

## 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt in VS Code and run:
```bat
.venv\Scripts\activate.bat
```

Install packages:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Generate the dataset

```powershell
python generate_dataset.py
```

Creates:
`data/synthetic_cardiovascular_hourly.csv`

It simulates 120 people with 14 days of hourly summaries each. Each patient's baseline is held stable for the demo. Patterns include normal variation, multisignal shifts, recovery, and missing readings.

Labels:
- `0`: normal variation in this synthetic simulation
- `1`: synthetic deviation scenario
- `-1`: all six measurements missing; excluded from supervised training

These labels are based on the generator's scenario design. They are not real patient outcomes.

## 4. Train and evaluate

```powershell
python train_model.py
```

Outputs:
- `models/deviation_model.joblib`
- `models/evaluation_metrics.json`

The split is by patient, so rows from a test patient do not appear in training. Review precision, recall, F1 and the confusion matrix, not accuracy alone. Results only describe this synthetic dataset.

## 5. Run the alert-rule demo

```powershell
python demo_alerts.py
```

It prints model outputs for a simulated patient and marks family-alert eligibility after three consecutive positive hourly assessments. This demo does not send notifications. A production backend must verify authorization, consent, delivery settings, duplicate suppression and persistence.

## Project files

- `generate_dataset.py` — synthetic CSV generator and feature engineering
- `train_model.py` — patient-separated training and evaluation
- `demo_alerts.py` — sample inference and persistence-gated alert eligibility
- `requirements.txt` — dependencies

## Suggested integration contract for FastAPI

Have your teammate expose an endpoint such as `POST /twin/assess` accepting the latest readings and baseline-relative features. Return a JSON object with:
- `deviation_state`
- `model_confidence` (clearly labeled as model classification confidence)
- `contributing_measurements`
- `explanation`
- `consecutive_positive_hours`
- `family_alert_eligible`

The backend, not the Flutter client, should enforce authorization and alert persistence.

## Important implementation note

The included training pipeline is a fast hackathon starting point. Before using real data, define clinically reviewed labels, units, data quality checks, baseline-calibration rules, time-aware validation, and prospective evaluation with qualified clinical oversight. Never use synthetic performance claims as clinical validation.
