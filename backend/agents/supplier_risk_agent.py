"""
Supplier Risk & Selection Agent

Responsible for:
- Loading supply-chain data
- Creating supplier-level features
- Calculating supplier risk scores
- Ranking suppliers by risk
- Calculating supplier selection scores
- Generating supplier recommendations
"""

from pathlib import Path

import pandas as pd


class SupplierRiskAgent:
    """AI agent responsible for supplier risk and selection analysis."""

    def __init__(self):
        self.name = "Supplier Risk & Selection Agent"

        self.data_path = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "raw"
            / "supply_chain_dataset1.csv"
        )

    def load_data(self):
        """Load the supply-chain dataset."""

        return pd.read_csv(self.data_path)

    def build_supplier_features(self, df):
        """Create supplier-level performance features."""

        supplier_data = (
            df.groupby("Supplier_ID")
            .agg(
                Records=("Supplier_ID", "size"),
                Avg_Lead_Time=("Supplier_Lead_Time_Days", "mean"),
                Avg_Cost=("Unit_Cost", "mean"),
                Avg_Order_Qty=("Order_Quantity", "mean"),
                Avg_Inventory=("Inventory_Level", "mean"),
                Avg_Demand=("Units_Sold", "mean"),
            )
            .reset_index()
        )

        supplier_data["Lead_Time_Risk"] = (
            supplier_data["Avg_Lead_Time"]
            / supplier_data["Avg_Lead_Time"].max()
        )

        supplier_data["Cost_Risk"] = (
            supplier_data["Avg_Cost"]
            / supplier_data["Avg_Cost"].max()
        )

        supplier_data["Inventory_Risk"] = (
            1
            - (
                supplier_data["Avg_Inventory"]
                / supplier_data["Avg_Inventory"].max()
            )
        )

        supplier_data["Demand_Exposure"] = (
            supplier_data["Avg_Demand"]
            / supplier_data["Avg_Demand"].max()
        )

        return supplier_data

    def calculate_risk(self, supplier_data):
        """Calculate supplier risk score."""

        supplier_data["Risk_Score"] = (
            supplier_data["Lead_Time_Risk"] * 0.40
            + supplier_data["Cost_Risk"] * 0.35
            + supplier_data["Inventory_Risk"] * 0.25
        ) * 100

        supplier_data["Risk_Category"] = pd.cut(
            supplier_data["Risk_Score"],
            bins=[-1, 40, 70, 101],
            labels=["Low", "Medium", "High"],
        )

        return supplier_data

    def calculate_selection_score(self, supplier_data):
        """Calculate supplier selection score."""

        max_lead_time = supplier_data["Avg_Lead_Time"].max()
        max_cost = supplier_data["Avg_Cost"].max()

        supplier_data["Lead_Time_Efficiency"] = (
            1
            - supplier_data["Avg_Lead_Time"]
            / max_lead_time
        )

        supplier_data["Cost_Efficiency"] = (
            1
            - supplier_data["Avg_Cost"]
            / max_cost
        )

        supplier_data["Risk_Safety"] = (
            1
            - supplier_data["Risk_Score"] / 100
        )

        supplier_data["Selection_Score"] = (
            supplier_data["Risk_Safety"] * 0.50
            + supplier_data["Lead_Time_Efficiency"] * 0.25
            + supplier_data["Cost_Efficiency"] * 0.25
        ) * 100

        return supplier_data

    def rank_suppliers(self, supplier_data):
        """Rank suppliers for selection."""

        return supplier_data.sort_values(
            "Selection_Score",
            ascending=False,
        ).reset_index(drop=True)

    def generate_recommendations(self, supplier_data):
        """Generate supplier recommendations."""

        recommendations = []

        for _, row in supplier_data.iterrows():

            if row["Risk_Category"] == "High":
                recommendation = (
                    "High risk. Review supplier and consider alternate sourcing."
                )

            elif row["Selection_Score"] >= 50:
                recommendation = (
                    "Suitable candidate. Monitor performance and lead time."
                )

            else:
                recommendation = (
                    "Use with monitoring and compare against alternatives."
                )

            recommendations.append(recommendation)

        supplier_data["Recommendation"] = recommendations

        return supplier_data

    def run(self):
        """Run the complete supplier risk and selection analysis."""

        df = self.load_data()

        supplier_data = self.build_supplier_features(df)

        supplier_data = self.calculate_risk(
            supplier_data
        )

        supplier_data = self.calculate_selection_score(
            supplier_data
        )

        supplier_data = self.rank_suppliers(
            supplier_data
        )

        supplier_data = self.generate_recommendations(
            supplier_data
        )

        return supplier_data


if __name__ == "__main__":

    agent = SupplierRiskAgent()

    results = agent.run()

    print("Agent:", agent.name)

    print(
        "\nSuppliers analyzed:",
        len(results),
    )

    print("\nSupplier Selection Analysis:")

    print(
        results[
            [
                "Supplier_ID",
                "Risk_Score",
                "Risk_Category",
                "Selection_Score",
                "Recommendation",
            ]
        ].round(2).to_string(index=False)
    )

    print("\nTop Supplier Candidates:")

    print(
        results[
            [
                "Supplier_ID",
                "Selection_Score",
                "Risk_Category",
            ]
        ]
        .head(3)
        .round(2)
        .to_string(index=False)
    )