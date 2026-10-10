# AI-Powered Supply Chain Intelligent System

A local supply-chain analytics dashboard built with React/Vite and FastAPI. It combines six operational analysis agents with a data-grounded, rule-based question-answering assistant and an interactive What-If scenario simulator.

> **Implementation note:** The assistant currently uses keyword rules and project CSV outputs to generate responses. It is not an LLM-powered chatbot. The What-If simulator is a deterministic scenario engine using the project's inventory and workforce data and assumptions.

## Project objectives

- Forecast product demand from historical supply-chain data.
- Analyze supplier risk and rank suppliers by risk score.
- Identify inventory levels requiring monitoring or replenishment.
- Summarize workforce planning requirements.
- Analyze warehouse-level propagated risk.
- Prioritize warehouses and present operational recommendations.
- Answer supported natural-language questions using existing agent outputs.
- Simulate changes in demand, supplier lead time, and inventory to estimate inventory and workforce impacts.

## Implemented features

### Six analysis agents

1. **Demand Forecasting** — returns forecast samples, row count, and evaluation metrics.
2. **Supplier Risk** — returns supplier risk results and rankings.
3. **Inventory Optimization** — returns inventory status and replenishment information.
4. **Workforce Intelligence** — summarizes workforce planning outputs.
5. **Risk Propagation** — returns propagated risk information by warehouse.
6. **Decision Intelligence** — returns warehouse priority scores, risk signals, and recommended actions.

### Supply Chain Assistant

The assistant loads the project's decision, risk, inventory, supplier, and workforce CSV outputs. Its `ask()` method uses predefined keyword rules to route questions to data-grounded response functions. Example questions include:

- Which warehouse needs attention?
- Why is WH_4 high priority?
- Which suppliers are risky?
- What inventory needs replenishment?
- What are today's recommended actions?
- What is the workforce status?

The assistant should be described as a **rule-based, data-grounded assistant**, not as generative AI or an LLM integration.

### What-If Scenario Simulator

The simulator accepts three percentage changes:

- `demand_change_pct`
- `lead_time_change_pct`
- `inventory_change_pct`

It calculates inventory and workforce impacts and returns recommendations. A local scenario test was run with demand +15%, supplier lead time +20%, and inventory -10%. The observed output reported 250 total locations, 14 critical items, 42 reorder items, 56 attention items (compared with 6 current attention locations), average scenario inventory of 410.47, average scenario reorder point of 272.43, and an additional peak workforce requirement of 5 workers. These are scenario outputs for the current data and assumptions, not universal guarantees.

## Architecture

```text
React + Vite dashboard
        |
        | HTTP requests (localhost)
        v
FastAPI application
        |
        +-- Demand Forecasting
        +-- Supplier Risk
        +-- Inventory Optimization
        +-- Workforce Intelligence
        +-- Risk Propagation
        +-- Decision Intelligence
        +-- Rule-based Supply Chain Assistant
        +-- What-If Scenario Simulator
        |
        v
CSV datasets and saved model files
```

## Technology stack

- **Frontend:** React, Vite, Recharts, Lucide React
- **Backend:** Python, FastAPI, Uvicorn
- **Data/ML:** pandas, NumPy, scikit-learn, joblib, XGBoost
- **Visualization:** Recharts
- **Data files:** CSV inputs and agent outputs; a saved XGBoost model is used by demand forecasting

## Project layout

```text
AI_Supply_Chain/
├── backend/
│   ├── agents/
│   │   ├── genai_assistant.py
│   │   └── what_if_simulator.py
│   ├── api/
│   ├── data/
│   ├── database/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── main.py
│   └── requirements.txt
├── data/
│   ├── raw/
│   │   └── supply_chain_dataset1.csv
│   ├── supplier_risk_features.csv
│   ├── inventory_optimization_results.csv
│   ├── workforce_intelligence_results.csv
│   ├── risk_propagation_results.csv
│   └── decision_intelligence_results.csv
├── frontend/
│   └── src/
│       └── App.jsx
├── ml/
│   └── demand_forecasting/
│       └── models/
│           └── demand_historical_xgboost.pkl
├── docs/
├── notebooks/
├── README.md
└── START_DASHBOARD.bat
```

Some files or directory names can differ as the project evolves; the backend's current code and referenced data paths are the source of truth.

## Run locally

### Option A: Use the Windows launcher

1. Keep `START_DASHBOARD.bat` in the project root.
2. Double-click it (or the desktop shortcut that points to it).
3. Keep the backend and frontend command windows open while using the dashboard.
4. Open `http://localhost:5174/` if the browser does not open automatically.

### Option B: Start the backend and frontend separately

Run these commands from the project root in separate terminals.

**Backend**

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --log-level info
```

**Frontend**

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

If frontend dependencies are already installed, `npm install` does not need to be repeated unless dependencies change.

## API endpoints

The following endpoints were verified in local testing:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health status |
| GET | `/api/data-validation` | Dataset validation summary |
| GET | `/api/demand-forecast` | Demand forecast outputs and evaluation |
| GET | `/api/supplier-risk` | Supplier risk outputs |
| GET | `/api/inventory-optimization` | Inventory and replenishment outputs |
| GET | `/api/workforce-intelligence` | Workforce analysis outputs |
| GET | `/api/risk-propagation` | Risk propagation outputs |
| GET | `/api/decision-intelligence` | Warehouse decisions and priorities |
| POST | `/api/assistant` | Ask the rule-based, data-grounded assistant |
| POST | `/api/what-if` | Run an inventory/workforce scenario |

### Example: assistant request

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8002/api/assistant" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"question":"Why is WH_4 high priority?"}'
```

### Example: What-If request

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8002/api/what-if" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"demand_change_pct":15,"lead_time_change_pct":20,"inventory_change_pct":-10}'
```

## Verification status

The following local checks have been performed during development:

- The eight original GET API endpoints returned successful responses.
- The assistant module ran its built-in example questions and returned data-grounded answers.
- The What-If simulator ran its built-in scenario successfully.
- `POST /api/assistant` returned a response for a warehouse-priority question.
- `POST /api/what-if` returned inventory/workforce scenario results and recommendations.
- The dashboard displayed the assistant and What-If panels, including inventory status counts and workforce impacts.

These are manual local checks, not a substitute for an automated test suite. Run the checks again after future code changes.

## Current limitations and future work

- The assistant is rule-based and does not currently use an external LLM provider.
- The simulator uses the current CSV outputs and deterministic assumptions; validate assumptions before using results for real operational decisions.
- Add automated backend/frontend tests and stronger input-validation coverage.
- Consider a real LLM integration only if required, with API keys kept in environment variables and never committed to Git.
- Further improve error handling, accessibility, and dashboard presentation polish.

## Data and usage notes

- Keep API keys, passwords, credentials, and `.env` files out of Git.
- The local `localhost` URLs work on the computer running the servers; they are not public web addresses.
- Outputs depend on the current CSV data, saved model, and implementation assumptions.
- This project is a prototype for academic demonstration and should not be treated as a production supply-chain decision system without additional validation.
