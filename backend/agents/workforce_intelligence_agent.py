import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# Workforce Intelligence Agent
# Demand-Based Workforce Planning
# ============================================================

DATA_PATH = Path("data/raw/supply_chain_dataset1.csv")
OUTPUT_PATH = Path("data/workforce_intelligence_results.csv")


# ------------------------------------------------------------
# Configurable workforce planning assumptions
# ------------------------------------------------------------

UNITS_PER_WORKER_PER_DAY = 50


def load_data():
    """Load and validate the supply chain dataset."""

    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "Date",
        "Warehouse_ID",
        "SKU_ID",
        "Units_Sold",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    return df


def calculate_workforce_requirements(df):
    """
    Estimate warehouse workforce requirements
    from daily demand.

    Note:
    This dataset does not contain employee or labor data.
    Therefore, workforce capacity is treated as a
    configurable planning assumption.
    """

    # --------------------------------------------------------
    # Aggregate demand at warehouse-day level
    # --------------------------------------------------------

    daily = (
        df.groupby(
            ["Date", "Warehouse_ID"]
        )
        .agg(
            Daily_Demand=("Units_Sold", "sum"),
            Active_SKUs=("SKU_ID", "nunique"),
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Calculate rolling demand indicators
    # --------------------------------------------------------

    daily["Date"] = pd.to_datetime(daily["Date"])

    daily = daily.sort_values(
        ["Warehouse_ID", "Date"]
    )

    daily["Demand_7D_Avg"] = (
        daily.groupby("Warehouse_ID")["Daily_Demand"]
        .transform(
            lambda x: x.rolling(
                7,
                min_periods=1
            ).mean()
        )
    )

    daily["Demand_7D_STD"] = (
        daily.groupby("Warehouse_ID")["Daily_Demand"]
        .transform(
            lambda x: x.rolling(
                7,
                min_periods=2
            ).std()
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # Estimate workers required
    # --------------------------------------------------------

    daily["Required_Workers"] = np.ceil(
        daily["Daily_Demand"]
        / UNITS_PER_WORKER_PER_DAY
    )

    daily["Workers_for_Avg_Demand"] = np.ceil(
        daily["Demand_7D_Avg"]
        / UNITS_PER_WORKER_PER_DAY
    )

    # --------------------------------------------------------
    # Estimate workload pressure
    #
    # Compare current demand with recent 7-day demand.
    # --------------------------------------------------------

    daily["Workload_Index"] = (
        daily["Daily_Demand"]
        / daily["Demand_7D_Avg"].replace(0, np.nan)
    )

    # --------------------------------------------------------
    # Demand variability
    # --------------------------------------------------------

    daily["Demand_Variability"] = (
        daily["Demand_7D_STD"]
        / daily["Demand_7D_Avg"].replace(0, np.nan)
    )

    daily["Demand_Variability"] = (
        daily["Demand_Variability"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    # --------------------------------------------------------
    # Workforce status
    # --------------------------------------------------------

    def classify_workforce(row):

        workload = row["Workload_Index"]

        if workload >= 1.25:
            return "High Pressure"

        elif workload >= 1.10:
            return "Monitor"

        elif workload <= 0.85:
            return "Underutilized"

        return "Adequate"

    daily["Workforce_Status"] = daily.apply(
        classify_workforce,
        axis=1
    )

    # --------------------------------------------------------
    # Staffing recommendation
    # --------------------------------------------------------

    def generate_recommendation(row):

        status = row["Workforce_Status"]

        workers = int(
            row["Required_Workers"]
        )

        if status == "High Pressure":
            return (
                f"High workload pressure. "
                f"Plan approximately {workers} workers "
                f"or additional shift capacity."
            )

        elif status == "Monitor":
            return (
                f"Workload is above recent average. "
                f"Monitor staffing and consider "
                f"{workers} workers."
            )

        elif status == "Underutilized":
            return (
                f"Demand is below recent average. "
                f"Review workforce utilization."
            )

        return (
            f"Workforce capacity appears adequate. "
            f"Plan approximately {workers} workers."
        )

    daily["Recommendation"] = daily.apply(
        generate_recommendation,
        axis=1
    )

    # --------------------------------------------------------
    # Round values
    # --------------------------------------------------------

    numeric_columns = daily.select_dtypes(
        include=["float64", "float32"]
    ).columns

    daily[numeric_columns] = (
        daily[numeric_columns].round(2)
    )

    return daily


def create_warehouse_summary(results):
    """Create warehouse-level workforce summary."""

    summary = (
        results.groupby("Warehouse_ID")
        .agg(
            Avg_Daily_Demand=("Daily_Demand", "mean"),
            Peak_Daily_Demand=("Daily_Demand", "max"),
            Avg_Required_Workers=(
                "Required_Workers",
                "mean"
            ),
            Peak_Required_Workers=(
                "Required_Workers",
                "max"
            ),
            Avg_Demand_Variability=(
                "Demand_Variability",
                "mean"
            ),
        )
        .reset_index()
    )

    summary["Avg_Required_Workers"] = (
        summary["Avg_Required_Workers"]
        .round(0)
        .astype(int)
    )

    summary["Peak_Required_Workers"] = (
        summary["Peak_Required_Workers"]
        .astype(int)
    )

    return summary


def main():

    print("=" * 70)
    print("WORKFORCE INTELLIGENCE AGENT")
    print("Demand-Based Workforce Planning")
    print("=" * 70)

    df = load_data()

    print(f"Dataset rows: {len(df)}")
    print(f"Warehouses: {df['Warehouse_ID'].nunique()}")
    print(f"SKUs: {df['SKU_ID'].nunique()}")

    print(
        f"Planning assumption: "
        f"{UNITS_PER_WORKER_PER_DAY} units/worker/day"
    )

    # Calculate workforce requirements
    results = calculate_workforce_requirements(df)

    # Create warehouse summary
    summary = create_warehouse_summary(results)

    # Create output directory
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save detailed results
    results.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # --------------------------------------------------------
    # Display sample
    # --------------------------------------------------------

    print("\nDaily Workforce Analysis")
    print("-" * 70)

    print(
        results[
            [
                "Date",
                "Warehouse_ID",
                "Daily_Demand",
                "Demand_7D_Avg",
                "Required_Workers",
                "Workload_Index",
                "Workforce_Status",
            ]
        ]
        .head(15)
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # Status distribution
    # --------------------------------------------------------

    print("\nWorkforce Status Distribution")
    print("-" * 70)

    print(
        results["Workforce_Status"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # Warehouse summary
    # --------------------------------------------------------

    print("\nWarehouse Workforce Summary")
    print("-" * 70)

    print(
        summary.to_string(index=False)
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print("\nOutput saved to:")
    print(OUTPUT_PATH)

    print("=" * 70)


if __name__ == "__main__":
    main()