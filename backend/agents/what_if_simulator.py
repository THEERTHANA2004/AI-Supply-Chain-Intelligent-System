from pathlib import Path
import math
import pandas as pd


class WhatIfSimulator:
    """
    Supply Chain What-If Simulation Engine.

    Simulates the impact of changes in:
    - Demand
    - Supplier lead time
    - Inventory levels

    The simulator uses the same explainable inventory and
    workforce planning assumptions used by the project agents.
    """

    UNITS_PER_WORKER_PER_DAY = 50
    SAFETY_STOCK_Z = 1.65

    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.data_dir = self.project_root / "data"

        self.inventory_file = (
            self.data_dir / "inventory_optimization_results.csv"
        )

        self.workforce_file = (
            self.data_dir / "workforce_intelligence_results.csv"
        )

        self.inventory = self._load_csv(self.inventory_file)
        self.workforce = self._load_csv(self.workforce_file)

    def _load_csv(self, file_path):
        """Load a CSV file safely."""

        if not file_path.exists():
            return pd.DataFrame()

        return pd.read_csv(file_path)

    def _safe_float(self, value, default=0.0):
        """Safely convert a value to float."""

        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def _status(self, inventory, reorder_point):
        """
        Determine inventory status using the same policy
        as the Inventory Optimization Agent.
        """

        if reorder_point <= 0:
            return "Healthy"

        ratio = inventory / reorder_point

        if ratio <= 0.75:
            return "Critical"

        if ratio <= 1.0:
            return "Reorder"

        if ratio <= 1.50:
            return "Monitor"

        return "Healthy"

    def simulate_inventory(
        self,
        demand_change_pct=0,
        lead_time_change_pct=0,
        inventory_change_pct=0
    ):
        """
        Simulate system-wide inventory impact.

        Parameters are percentage changes.

        Example:
        demand_change_pct=15
        means demand increases by 15%.
        """

        if self.inventory.empty:
            return {
                "status": "error",
                "message": "Inventory optimization data is not available."
            }

        df = self.inventory.copy()

        demand_multiplier = 1 + (
            demand_change_pct / 100
        )

        lead_time_multiplier = 1 + (
            lead_time_change_pct / 100
        )

        inventory_multiplier = 1 + (
            inventory_change_pct / 100
        )

        df["Scenario_Demand"] = (
            df["Avg_Demand"] * demand_multiplier
        )

        df["Scenario_Lead_Time"] = (
            df["Avg_Lead_Time"] * lead_time_multiplier
        )

        df["Scenario_Inventory"] = (
            df["Current_Inventory"] * inventory_multiplier
        )

        # Scenario lead-time demand
        df["Scenario_Lead_Time_Demand"] = (
            df["Scenario_Demand"]
            * df["Scenario_Lead_Time"]
        )

        # Safety stock changes with demand variability
        df["Scenario_Demand_STD"] = (
            df["Demand_STD"] * demand_multiplier
        )

        df["Scenario_Safety_Stock"] = (
            self.SAFETY_STOCK_Z
            * df["Scenario_Demand_STD"]
            * df["Scenario_Lead_Time"].pow(0.5)
        )

        # Scenario reorder point
        df["Scenario_Reorder_Point"] = (
            df["Scenario_Lead_Time_Demand"]
            + df["Scenario_Safety_Stock"]
        )

        # Inventory gap
        df["Scenario_Inventory_Gap"] = (
            df["Scenario_Inventory"]
            - df["Scenario_Reorder_Point"]
        )

        # Inventory status
        df["Scenario_Status"] = df.apply(
            lambda row: self._status(
                row["Scenario_Inventory"],
                row["Scenario_Reorder_Point"]
            ),
            axis=1
        )

        return df

    def summarize_inventory_impact(self, df):
        """Create a system-level inventory summary."""

        if df.empty:
            return {}

        status_counts = (
            df["Scenario_Status"]
            .value_counts()
            .to_dict()
        )

        current_attention = (
            self.inventory["Inventory_Status"]
            .isin(["Critical", "Reorder"])
            .sum()
        )

        scenario_attention = (
            df["Scenario_Status"]
            .isin(["Critical", "Reorder"])
            .sum()
        )

        critical_items = (
            df["Scenario_Status"] == "Critical"
        ).sum()

        reorder_items = (
            df["Scenario_Status"] == "Reorder"
        ).sum()

        avg_reorder_point = (
            df["Scenario_Reorder_Point"].mean()
        )

        avg_inventory = (
            df["Scenario_Inventory"].mean()
        )

        return {
            "total_locations": len(df),
            "critical_items": int(critical_items),
            "reorder_items": int(reorder_items),
            "attention_items": int(scenario_attention),
            "current_attention_items": int(current_attention),
            "attention_change": int(
                scenario_attention - current_attention
            ),
            "average_inventory": round(
                avg_inventory,
                2
            ),
            "average_reorder_point": round(
                avg_reorder_point,
                2
            ),
            "status_distribution": status_counts
        }

    def simulate_workforce(self, demand_change_pct=0):
        """
        Estimate workforce requirement under a demand scenario.
        """

        if self.workforce.empty:
            return {
                "status": "error",
                "message": "Workforce data is not available."
            }

        df = self.workforce.copy()

        multiplier = 1 + (
            demand_change_pct / 100
        )

        # Current daily demand is used as the workload baseline.
        if "Daily_Demand" in df.columns:
            df["Scenario_Demand"] = (
                df["Daily_Demand"] * multiplier
            )
        else:
            df["Scenario_Demand"] = (
                df["Required_Workers"]
                * self.UNITS_PER_WORKER_PER_DAY
                * multiplier
            )

        df["Scenario_Required_Workers"] = (
            df["Scenario_Demand"]
            / self.UNITS_PER_WORKER_PER_DAY
        ).apply(math.ceil)

        current_peak = int(
            self.workforce["Required_Workers"].max()
        )

        scenario_peak = int(
            df["Scenario_Required_Workers"].max()
        )

        return {
            "current_peak_workers": current_peak,
            "scenario_peak_workers": scenario_peak,
            "additional_peak_workers": (
                scenario_peak - current_peak
            )
        }

    def generate_recommendation(
        self,
        inventory_summary,
        workforce_summary
    ):
        """Generate an explainable scenario recommendation."""

        attention_change = inventory_summary.get(
            "attention_change",
            0
        )

        additional_workers = workforce_summary.get(
            "additional_peak_workers",
            0
        )

        critical_items = inventory_summary.get(
            "critical_items",
            0
        )

        recommendations = []

        if critical_items > 0:
            recommendations.append(
                "Prioritize replenishment for critical inventory."
            )

        if attention_change > 0:
            recommendations.append(
                f"Inventory attention increases by "
                f"{attention_change} locations."
            )

        elif attention_change < 0:
            recommendations.append(
                f"Inventory attention decreases by "
                f"{abs(attention_change)} locations."
            )

        if additional_workers > 0:
            recommendations.append(
                f"Peak workforce requirement increases by "
                f"{additional_workers} workers."
            )

        elif additional_workers < 0:
            recommendations.append(
                f"Peak workforce requirement decreases by "
                f"{abs(additional_workers)} workers."
            )

        if not recommendations:
            recommendations.append(
                "Scenario impact is limited; continue normal monitoring."
            )

        return recommendations

    def run_scenario(
        self,
        demand_change_pct=0,
        lead_time_change_pct=0,
        inventory_change_pct=0
    ):
        """
        Run a complete what-if scenario.
        """

        inventory_result = self.simulate_inventory(
            demand_change_pct=demand_change_pct,
            lead_time_change_pct=lead_time_change_pct,
            inventory_change_pct=inventory_change_pct
        )

        if isinstance(inventory_result, dict):
            return inventory_result

        inventory_summary = self.summarize_inventory_impact(
            inventory_result
        )

        workforce_summary = self.simulate_workforce(
            demand_change_pct=demand_change_pct
        )

        recommendations = self.generate_recommendation(
            inventory_summary,
            workforce_summary
        )

        return {
            "scenario": {
                "demand_change_pct": demand_change_pct,
                "lead_time_change_pct": lead_time_change_pct,
                "inventory_change_pct": inventory_change_pct
            },
            "inventory": inventory_summary,
            "workforce": workforce_summary,
            "recommendations": recommendations
        }


if __name__ == "__main__":

    simulator = WhatIfSimulator()

    print("=" * 70)
    print("SUPPLY CHAIN WHAT-IF SIMULATOR")
    print("=" * 70)

    print("\nScenario:")
    print("Demand +15%")
    print("Supplier Lead Time +20%")
    print("Inventory -10%")

    result = simulator.run_scenario(
        demand_change_pct=15,
        lead_time_change_pct=20,
        inventory_change_pct=-10
    )

    print("\nINVENTORY IMPACT")
    print("-" * 70)

    inventory = result["inventory"]

    print(
        f"Current attention locations: "
        f"{inventory['current_attention_items']}"
    )

    print(
        f"Scenario attention locations: "
        f"{inventory['attention_items']}"
    )

    print(
        f"Change in attention: "
        f"{inventory['attention_change']}"
    )

    print(
        f"Critical inventory items: "
        f"{inventory['critical_items']}"
    )

    print(
        f"Average scenario inventory: "
        f"{inventory['average_inventory']}"
    )

    print(
        f"Average scenario reorder point: "
        f"{inventory['average_reorder_point']}"
    )

    print("\nWORKFORCE IMPACT")
    print("-" * 70)

    workforce = result["workforce"]

    print(
        f"Current peak workers: "
        f"{workforce['current_peak_workers']}"
    )

    print(
        f"Scenario peak workers: "
        f"{workforce['scenario_peak_workers']}"
    )

    print(
        f"Additional peak workers: "
        f"{workforce['additional_peak_workers']}"
    )

    print("\nRECOMMENDATIONS")
    print("-" * 70)

    for recommendation in result["recommendations"]:
        print(f"- {recommendation}")

    print("\n" + "=" * 70)
    print("WHAT-IF SIMULATION COMPLETED")
    print("=" * 70)