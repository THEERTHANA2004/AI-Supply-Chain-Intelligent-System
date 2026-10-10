from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.data.data_validator import load_and_validate_data

from backend.agents.demand_forecasting_agent import (
    DemandForecastingAgent,
)

from backend.agents.supplier_risk_agent import (
    SupplierRiskAgent,
)

from backend.agents.inventory_optimization_agent import (
    load_data as load_inventory_data,
    calculate_inventory_policy,
)

from backend.agents.workforce_intelligence_agent import (
    load_data as load_workforce_data,
    calculate_workforce_requirements,
)

from backend.agents.risk_propagation_agent import (
    load_data as load_risk_data,
    calculate_supplier_risk,
    calculate_inventory_risk,
    calculate_workforce_risk,
    build_risk_propagation,
)

from backend.agents.decision_intelligence_agent import (
    load_data as load_decision_data,
    create_decisions,
)


# SUPPLY_CHAIN_INTERACTIVE_FEATURES_V1
from pydantic import BaseModel, Field
from backend.agents.genai_assistant import GenAIAssistant
from backend.agents.what_if_simulator import WhatIfSimulator

class AssistantQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)

class WhatIfScenarioRequest(BaseModel):
    demand_change_pct: float = Field(default=15, ge=-100, le=500)
    lead_time_change_pct: float = Field(default=20, ge=-90, le=500)
    inventory_change_pct: float = Field(default=-10, ge=-100, le=500)

app = FastAPI(
    title="Supply Chain AI API",
    description="AI-Powered Multi-Agent Supply Chain Intelligence System",
    version="1.0.0",
)


# Allow the Vite frontend on ports 5173 and 5174.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Supply Chain AI API is running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/demand-forecast")
def demand_forecast():
    agent = DemandForecastingAgent()

    data = agent.load_data()
    data = agent.prepare_features(data)

    predictions = agent.predict(data)
    evaluation = agent.evaluate(predictions)

    return {
        "agent": agent.name,
        "rows": len(predictions),
        "evaluation": evaluation,
        "sample_predictions": predictions[
            [
                "Date",
                "SKU_ID",
                "Warehouse_ID",
                "Units_Sold",
                "Predicted_Demand",
            ]
        ].tail(10).to_dict(orient="records"),
    }


@app.get("/api/supplier-risk")
def supplier_risk():
    agent = SupplierRiskAgent()
    results = agent.run()

    return {
        "agent": agent.name,
        "suppliers_analyzed": len(results),
        "suppliers": results[
            [
                "Supplier_ID",
                "Risk_Score",
                "Risk_Category",
                "Selection_Score",
                "Recommendation",
            ]
        ].to_dict(orient="records"),
    }


@app.get("/api/inventory-optimization")
def inventory_optimization():
    df = load_inventory_data()
    results = calculate_inventory_policy(df)

    return {
        "agent": "Inventory Optimization Agent",
        "locations_analyzed": len(results),
        "status_summary": results[
            "Inventory_Status"
        ].value_counts().to_dict(),
        "inventory": results[
            [
                "SKU_ID",
                "Warehouse_ID",
                "Current_Inventory",
                "Recommended_Reorder_Point",
                "Recommended_Order_Qty",
                "Inventory_Status",
                "Recommendation",
            ]
        ].to_dict(orient="records"),
    }


@app.get("/api/workforce-intelligence")
def workforce_intelligence():
    df = load_workforce_data()
    results = calculate_workforce_requirements(df)

    return {
        "agent": "Workforce Intelligence Agent",
        "days_analyzed": len(results),
        "status_summary": results[
            "Workforce_Status"
        ].value_counts().to_dict(),
        "workforce": results[
            [
                "Date",
                "Warehouse_ID",
                "Daily_Demand",
                "Required_Workers",
                "Workers_for_Avg_Demand",
                "Workload_Index",
                "Demand_Variability",
                "Workforce_Status",
                "Recommendation",
            ]
        ].to_dict(orient="records"),
    }


@app.get("/api/risk-propagation")
def risk_propagation():
    supplier, inventory, workforce = load_risk_data()

    supplier = calculate_supplier_risk(supplier)
    inventory = calculate_inventory_risk(inventory)
    workforce = calculate_workforce_risk(workforce)

    results = build_risk_propagation(
        supplier,
        inventory,
        workforce,
    )

    return {
        "agent": "Risk Propagation Agent",
        "warehouses_analyzed": len(results),
        "risk_summary": results[
            "Overall_Risk_Level"
        ].value_counts().to_dict(),
        "risk_propagation": results[
            [
                "Warehouse_ID",
                "Supplier_Risk_Exposure",
                "Avg_Inventory_Risk",
                "Avg_Workforce_Risk",
                "Propagated_Risk_Score",
                "Overall_Risk_Level",
                "Risk_Propagation_Explanation",
            ]
        ].to_dict(orient="records"),
    }


@app.get("/api/decision-intelligence")
def decision_intelligence():
    (
        demand,
        supplier,
        inventory,
        workforce,
        risk,
    ) = load_decision_data()

    decisions = create_decisions(
        demand,
        supplier,
        inventory,
        workforce,
        risk,
    )

    return {
        "agent": "Decision Intelligence Agent",
        "warehouses_analyzed": len(decisions),
        "priority_summary": decisions[
            "Decision_Priority"
        ].value_counts().to_dict(),
        "decisions": decisions[
            [
                "Warehouse_ID",
                "Propagated_Risk_Score",
                "Overall_Risk_Level",
                "Dominant_Risk_Signal",
                "Decision_Priority_Score",
                "Decision_Priority",
                "Decision_Confidence",
                "Average_Supplier_Risk",
                "High_Risk_Suppliers",
                "Action_Plan",
                "Why_This_Decision",
            ]
        ].to_dict(orient="records"),
    }


@app.get("/api/data-validation")
def data_validation():
    _, report = load_and_validate_data()

    return {
        "status": "valid" if report["valid"] else "invalid",
        "rows_loaded": report["total_rows"],
        "columns_loaded": report["total_columns"],
        "validation": report["checks"],
    }

# SUPPLY_CHAIN_INTERACTIVE_FEATURES_V1
@app.post("/api/assistant")
def ask_supply_chain_assistant(request: AssistantQuestionRequest):
    question = request.question.strip()
    if not question:
        return {
            "question": request.question,
            "answer": "Please enter a supply-chain question.",
            "assistant_type": "rule-based, data-grounded",
        }
    assistant = GenAIAssistant()
    return {
        "question": question,
        "answer": assistant.ask(question),
        "assistant_type": "rule-based, data-grounded",
    }

@app.post("/api/what-if")
def run_what_if_scenario(request: WhatIfScenarioRequest):
    simulator = WhatIfSimulator()
    return simulator.run_scenario(
        demand_change_pct=request.demand_change_pct,
        lead_time_change_pct=request.lead_time_change_pct,
        inventory_change_pct=request.inventory_change_pct,
    )
