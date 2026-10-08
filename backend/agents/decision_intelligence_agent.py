import pandas as pd
from pathlib import Path


# ============================================================
# Explainable Decision Intelligence Agent
# ============================================================

DEMAND_PATH = Path(
    "data/raw/supply_chain_dataset1.csv"
)

SUPPLIER_PATH = Path(
    "data/supplier_risk_features.csv"
)

INVENTORY_PATH = Path(
    "data/inventory_optimization_results.csv"
)

WORKFORCE_PATH = Path(
    "data/workforce_intelligence_results.csv"
)

RISK_PATH = Path(
    "data/risk_propagation_results.csv"
)

OUTPUT_PATH = Path(
    "data/decision_intelligence_results.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    demand = pd.read_csv(
        DEMAND_PATH
    )

    supplier = pd.read_csv(
        SUPPLIER_PATH
    )

    inventory = pd.read_csv(
        INVENTORY_PATH
    )

    workforce = pd.read_csv(
        WORKFORCE_PATH
    )

    risk = pd.read_csv(
        RISK_PATH
    )

    return (
        demand,
        supplier,
        inventory,
        workforce,
        risk
    )


# ============================================================
# DECISION ENGINE
# ============================================================

def create_decisions(
    demand,
    supplier,
    inventory,
    workforce,
    risk
):

    # --------------------------------------------------------
    # Demand intelligence
    # --------------------------------------------------------

    demand_summary = (
        demand.groupby("Warehouse_ID")
        .agg(
            Avg_Demand=(
                "Units_Sold",
                "mean"
            ),
            Peak_Demand=(
                "Units_Sold",
                "max"
            )
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Supplier intelligence
    # --------------------------------------------------------

    average_supplier_risk = (
        supplier["Risk_Score"]
        .mean()
    )

    high_risk_suppliers = (
        supplier[
            supplier["Risk_Category"] == "High"
        ]
        .shape[0]
    )

    # --------------------------------------------------------
    # Inventory intelligence
    # --------------------------------------------------------

    inventory_summary = (
        inventory.groupby("Warehouse_ID")
        .agg(
            Critical_Items=(
                "Inventory_Status",
                lambda x: (
                    x == "Critical"
                ).sum()
            ),
            Reorder_Items=(
                "Inventory_Status",
                lambda x: (
                    x == "Reorder"
                ).sum()
            ),
            Monitor_Items=(
                "Inventory_Status",
                lambda x: (
                    x == "Monitor"
                ).sum()
            )
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Workforce intelligence
    # --------------------------------------------------------

    workforce_summary = (
        workforce.groupby("Warehouse_ID")
        .agg(
            High_Pressure_Days=(
                "Workforce_Status",
                lambda x: (
                    x == "High Pressure"
                ).sum()
            ),
            Monitor_Days=(
                "Workforce_Status",
                lambda x: (
                    x == "Monitor"
                ).sum()
            )
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Merge intelligence layers
    # --------------------------------------------------------

    decisions = (
        demand_summary
        .merge(
            inventory_summary,
            on="Warehouse_ID",
            how="left"
        )
        .merge(
            workforce_summary,
            on="Warehouse_ID",
            how="left"
        )
        .merge(
            risk[
                [
                    "Warehouse_ID",
                    "Propagated_Risk_Score",
                    "Overall_Risk_Level"
                ]
            ],
            on="Warehouse_ID",
            how="left"
        )
    )

    # ========================================================
    # DECISION PRIORITY
    # ========================================================

    decisions["Decision_Priority_Score"] = (
        decisions["Propagated_Risk_Score"]
        + decisions["Critical_Items"] * 10
        + decisions["Reorder_Items"] * 5
        + decisions["High_Pressure_Days"] * 0.5
    )

    decisions["Decision_Priority_Score"] = (
        decisions[
            "Decision_Priority_Score"
        ]
        .round(2)
    )

    # --------------------------------------------------------
    # Priority classification
    # --------------------------------------------------------

    def classify_priority(score):

        if score >= 70:
            return "Immediate Action"

        elif score >= 50:
            return "High Priority"

        elif score >= 35:
            return "Monitor"

        return "Normal"

    decisions["Decision_Priority"] = (
        decisions[
            "Decision_Priority_Score"
        ]
        .apply(classify_priority)
    )

    # ========================================================
    # DOMINANT RISK SIGNAL
    # ========================================================

    def identify_dominant_risk(row):

        inventory_risk = (
            row["Critical_Items"] * 10
            + row["Reorder_Items"] * 5
        )

        workforce_risk = (
            row["High_Pressure_Days"] * 0.5
        )

        propagated_risk = (
            row["Propagated_Risk_Score"]
        )

        if inventory_risk >= workforce_risk:

            if inventory_risk > 0:
                return "Inventory Risk"

        if workforce_risk > 0:
            return "Workforce Pressure"

        if propagated_risk >= 35:
            return "Supply Chain Risk"

        return "No Dominant Risk"

    decisions["Dominant_Risk_Signal"] = (
        decisions.apply(
            identify_dominant_risk,
            axis=1
        )
    )

    # ========================================================
    # ACTION PLAN
    # ========================================================

    def generate_action_plan(row):

        actions = []

        if row["Critical_Items"] > 0:

            actions.append(
                "1. Replenish critical inventory immediately."
            )

        if row["Reorder_Items"] > 0:

            actions.append(
                "2. Review and execute pending reorder requirements."
            )

        if row["High_Pressure_Days"] > 0:

            actions.append(
                "3. Plan additional workforce or shift capacity."
            )

        if row["Overall_Risk_Level"] == "High":

            actions.append(
                "4. Review supplier alternatives and risk exposure."
            )

        if not actions:

            actions.append(
                "1. Continue normal monitoring and replenishment."
            )

        return " ".join(actions)

    decisions["Action_Plan"] = (
        decisions.apply(
            generate_action_plan,
            axis=1
        )
    )

    # ========================================================
    # DECISION CONFIDENCE
    # ========================================================

    def calculate_confidence(row):

        confidence = 60

        # Strong inventory signal
        if row["Critical_Items"] > 0:
            confidence += 15

        elif row["Reorder_Items"] > 0:
            confidence += 10

        # Strong workforce signal
        if row["High_Pressure_Days"] > 0:
            confidence += 10

        # Strong propagated risk signal
        if row["Propagated_Risk_Score"] >= 40:
            confidence += 10

        # Stable situation
        if row["Decision_Priority"] == "Normal":
            confidence += 5

        return min(
            confidence,
            95
        )

    decisions["Decision_Confidence"] = (
        decisions.apply(
            calculate_confidence,
            axis=1
        )
    )

    # ========================================================
    # EXPLAINABLE "WHY?"
    # ========================================================

    def generate_explanation(row):

        reasons = []

        # Inventory explanation
        if row["Critical_Items"] > 0:

            reasons.append(
                f"{int(row['Critical_Items'])} critical "
                f"inventory item(s) require attention."
            )

        elif row["Reorder_Items"] > 0:

            reasons.append(
                f"{int(row['Reorder_Items'])} inventory "
                f"item(s) are below the recommended reorder point."
            )

        else:

            reasons.append(
                "Inventory levels are generally stable."
            )

        # Workforce explanation
        if row["High_Pressure_Days"] > 0:

            reasons.append(
                f"{int(row['High_Pressure_Days'])} high-pressure "
                f"workforce day(s) were detected."
            )

        else:

            reasons.append(
                "Workforce capacity is generally stable."
            )

        # Risk explanation
        reasons.append(
            f"Propagated supply chain risk score is "
            f"{row['Propagated_Risk_Score']:.2f}."
        )

        return " ".join(reasons)

    decisions["Why_This_Decision"] = (
        decisions.apply(
            generate_explanation,
            axis=1
        )
    )

    # ========================================================
    # SYSTEM-LEVEL SUPPLIER INFORMATION
    # ========================================================

    decisions["Average_Supplier_Risk"] = round(
        average_supplier_risk,
        2
    )

    decisions["High_Risk_Suppliers"] = (
        high_risk_suppliers
    )

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    return decisions[
        [
            "Warehouse_ID",
            "Avg_Demand",
            "Peak_Demand",
            "Critical_Items",
            "Reorder_Items",
            "Monitor_Items",
            "High_Pressure_Days",
            "Monitor_Days",
            "Propagated_Risk_Score",
            "Overall_Risk_Level",
            "Dominant_Risk_Signal",
            "Decision_Priority_Score",
            "Decision_Priority",
            "Decision_Confidence",
            "Average_Supplier_Risk",
            "High_Risk_Suppliers",
            "Action_Plan",
            "Why_This_Decision"
        ]
    ]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("EXPLAINABLE DECISION INTELLIGENCE AGENT")
    print("=" * 70)

    (
        demand,
        supplier,
        inventory,
        workforce,
        risk
    ) = load_data()

    print(
        f"Demand records: {len(demand)}"
    )

    print(
        f"Supplier records: {len(supplier)}"
    )

    print(
        f"Inventory records: {len(inventory)}"
    )

    print(
        f"Workforce records: {len(workforce)}"
    )

    print(
        f"Risk records: {len(risk)}"
    )

    # --------------------------------------------------------
    # Generate decisions
    # --------------------------------------------------------

    decisions = create_decisions(
        demand,
        supplier,
        inventory,
        workforce,
        risk
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    decisions.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\nDecision Intelligence Results")
    print("-" * 70)

    print(
        decisions[
            [
                "Warehouse_ID",
                "Propagated_Risk_Score",
                "Dominant_Risk_Signal",
                "Decision_Priority_Score",
                "Decision_Priority",
                "Decision_Confidence"
            ]
        ].to_string(
            index=False
        )
    )

    print(
        "\nDecision Priority Distribution"
    )

    print("-" * 70)

    print(
        decisions[
            "Decision_Priority"
        ]
        .value_counts()
        .to_string()
    )

    print(
        "\nRecommended Actions"
    )

    print("-" * 70)

    for _, row in decisions.iterrows():

        print(
            f"{row['Warehouse_ID']}: "
            f"{row['Action_Plan']}"
        )

    print(
        "\nOutput saved to:"
    )

    print(
        OUTPUT_PATH
    )

    print("=" * 70)


if __name__ == "__main__":
    main()