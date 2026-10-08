import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# Inventory Optimization Agent
# ============================================================

DATA_PATH = Path("data/raw/supply_chain_dataset1.csv")
OUTPUT_PATH = Path("data/inventory_optimization_results.csv")


def load_data():
    """Load and validate the supply chain dataset."""

    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "SKU_ID",
        "Warehouse_ID",
        "Units_Sold",
        "Supplier_Lead_Time_Days",
        "Inventory_Level",
        "Reorder_Point",
        "Order_Quantity",
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


def calculate_inventory_policy(df):
    """
    Calculate inventory optimization metrics
    for each SKU-Warehouse combination.
    """

    # --------------------------------------------------------
    # Aggregate historical inventory and demand information
    # --------------------------------------------------------

    grouped = (
        df.groupby(["SKU_ID", "Warehouse_ID"])
        .agg(
            Avg_Demand=("Units_Sold", "mean"),
            Demand_STD=("Units_Sold", "std"),
            Avg_Lead_Time=("Supplier_Lead_Time_Days", "mean"),
            Current_Inventory=("Inventory_Level", "last"),
            Current_Reorder_Point=("Reorder_Point", "last"),
            Avg_Order_Qty=("Order_Quantity", "mean"),
        )
        .reset_index()
    )

    # Handle cases where standard deviation is unavailable
    grouped["Demand_STD"] = grouped["Demand_STD"].fillna(0)

    # --------------------------------------------------------
    # 1. Lead-time demand
    #
    # Expected demand during supplier lead time.
    # --------------------------------------------------------

    grouped["Lead_Time_Demand"] = (
        grouped["Avg_Demand"]
        * grouped["Avg_Lead_Time"]
    )

    # --------------------------------------------------------
    # 2. Safety stock
    #
    # Z = 1.65 approximately represents a 95% service level.
    #
    # Safety Stock =
    # Z × Demand Standard Deviation × sqrt(Lead Time)
    # --------------------------------------------------------

    SERVICE_LEVEL_Z = 1.65

    grouped["Safety_Stock"] = (
        SERVICE_LEVEL_Z
        * grouped["Demand_STD"]
        * np.sqrt(grouped["Avg_Lead_Time"])
    )

    # --------------------------------------------------------
    # 3. Recommended Reorder Point
    #
    # Reorder Point =
    # Lead-time demand + Safety stock
    # --------------------------------------------------------

    grouped["Recommended_Reorder_Point"] = (
        grouped["Lead_Time_Demand"]
        + grouped["Safety_Stock"]
    )

    # --------------------------------------------------------
    # 4. Recommended Order Quantity
    #
    # Use approximately one week of demand.
    #
    # We also compare it with the historical order quantity
    # so the recommendation does not fall below the supplier's
    # typical order size.
    # --------------------------------------------------------

    demand_cycle_qty = (
        grouped["Avg_Demand"] * 7
    )

    grouped["Recommended_Order_Qty"] = np.maximum(
        demand_cycle_qty,
        grouped["Avg_Order_Qty"]
    )

    grouped["Recommended_Order_Qty"] = (
        grouped["Recommended_Order_Qty"]
        .clip(lower=1)
        .round(0)
    )

    # --------------------------------------------------------
    # 5. Inventory gap
    #
    # Positive = inventory above recommended reorder point
    # Negative = inventory below recommended reorder point
    # --------------------------------------------------------

    grouped["Inventory_Gap"] = (
        grouped["Current_Inventory"]
        - grouped["Recommended_Reorder_Point"]
    )

    # --------------------------------------------------------
    # 6. Inventory coverage
    #
    # Number of days current inventory can support
    # average demand.
    # --------------------------------------------------------

    grouped["Inventory_Cover_Days"] = (
        grouped["Current_Inventory"]
        / grouped["Avg_Demand"].replace(0, np.nan)
    )

    # --------------------------------------------------------
    # 7. Inventory Status
    # --------------------------------------------------------

    def classify_inventory(row):

        inventory = row["Current_Inventory"]
        reorder_point = row["Recommended_Reorder_Point"]

        if inventory <= reorder_point * 0.75:
            return "Critical"

        elif inventory <= reorder_point:
            return "Reorder"

        elif inventory <= reorder_point * 1.50:
            return "Monitor"

        else:
            return "Healthy"

    grouped["Inventory_Status"] = grouped.apply(
        classify_inventory,
        axis=1
    )

    # --------------------------------------------------------
    # 8. Generate business recommendation
    # --------------------------------------------------------

    def generate_recommendation(row):

        status = row["Inventory_Status"]

        if status == "Critical":
            return (
                "Critical inventory level. "
                "Place replenishment order immediately."
            )

        elif status == "Reorder":
            return (
                "Inventory is below the recommended reorder point. "
                "Plan replenishment."
            )

        elif status == "Monitor":
            return (
                "Inventory is adequate but should be monitored "
                "against demand and lead time."
            )

        return (
            "Inventory level is healthy. "
            "Continue normal replenishment monitoring."
        )

    grouped["Recommendation"] = grouped.apply(
        generate_recommendation,
        axis=1
    )

    # --------------------------------------------------------
    # Round numerical values
    # --------------------------------------------------------

    numeric_columns = grouped.select_dtypes(
        include=["float64", "float32"]
    ).columns

    grouped[numeric_columns] = (
        grouped[numeric_columns].round(2)
    )

    return grouped


def main():

    print("=" * 70)
    print("INVENTORY OPTIMIZATION AGENT")
    print("=" * 70)

    # Load data
    df = load_data()

    print(f"Dataset rows: {len(df)}")
    print(f"SKUs: {df['SKU_ID'].nunique()}")
    print(f"Warehouses: {df['Warehouse_ID'].nunique()}")

    # Calculate inventory policy
    results = calculate_inventory_policy(df)

    # Create output directory if necessary
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save results
    results.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # --------------------------------------------------------
    # Display sample results
    # --------------------------------------------------------

    print("\nInventory Optimization Results")
    print("-" * 70)

    print(
        results[
            [
                "SKU_ID",
                "Warehouse_ID",
                "Current_Inventory",
                "Recommended_Reorder_Point",
                "Safety_Stock",
                "Recommended_Order_Qty",
                "Inventory_Status",
            ]
        ]
        .head(15)
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # Display status distribution
    # --------------------------------------------------------

    print("\nInventory Status Distribution")
    print("-" * 70)

    print(
        results["Inventory_Status"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # Display critical/reorder items
    # --------------------------------------------------------

    flagged = results[
        results["Inventory_Status"].isin(
            ["Critical", "Reorder"]
        )
    ]

    print("\nItems Requiring Replenishment Attention")
    print("-" * 70)

    if len(flagged) > 0:

        print(
            flagged[
                [
                    "SKU_ID",
                    "Warehouse_ID",
                    "Current_Inventory",
                    "Recommended_Reorder_Point",
                    "Recommended_Order_Qty",
                    "Inventory_Status",
                ]
            ].to_string(index=False)
        )

    else:
        print("No critical or reorder items found.")

    # --------------------------------------------------------
    # Output information
    # --------------------------------------------------------

    print("\nOutput saved to:")
    print(OUTPUT_PATH)

    print("=" * 70)


if __name__ == "__main__":
    main()