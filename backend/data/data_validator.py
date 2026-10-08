from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "supply_chain_dataset1.csv"

REQUIRED_COLUMNS = [
    "Date",
    "SKU_ID",
    "Warehouse_ID",
    "Supplier_ID",
    "Region",
    "Units_Sold",
    "Inventory_Level",
    "Supplier_Lead_Time_Days",
    "Reorder_Point",
    "Order_Quantity",
    "Unit_Cost",
    "Unit_Price",
    "Promotion_Flag",
    "Stockout_Flag",
    "Demand_Forecast",
]

NUMERIC_COLUMNS = [
    "Units_Sold",
    "Inventory_Level",
    "Supplier_Lead_Time_Days",
    "Reorder_Point",
    "Order_Quantity",
    "Unit_Cost",
    "Unit_Price",
    "Demand_Forecast",
]

NON_NEGATIVE_COLUMNS = [
    "Units_Sold",
    "Inventory_Level",
    "Supplier_Lead_Time_Days",
    "Reorder_Point",
    "Order_Quantity",
    "Unit_Cost",
    "Unit_Price",
    "Demand_Forecast",
]

BINARY_COLUMNS = [
    "Promotion_Flag",
    "Stockout_Flag",
]


# ---------------------------------------------------------
# Data Import
# ---------------------------------------------------------

def load_raw_data(file_path=RAW_DATA_PATH):
    """
    Load the raw supply-chain CSV dataset.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    return df


# ---------------------------------------------------------
# Required Column Validation
# ---------------------------------------------------------

def validate_required_columns(df):
    """
    Check whether all required columns exist.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        return False, missing_columns

    return True, []


# ---------------------------------------------------------
# Missing Value Validation
# ---------------------------------------------------------

def validate_missing_values(df):
    """
    Check for missing or blank values.
    """

    missing_counts = df[REQUIRED_COLUMNS].isnull().sum()

    missing_counts = missing_counts[
        missing_counts > 0
    ]

    return missing_counts.to_dict()


# ---------------------------------------------------------
# Numeric Data Validation
# ---------------------------------------------------------

def validate_numeric_columns(df):
    """
    Check whether numeric columns contain invalid values.
    """

    invalid_columns = {}

    for column in NUMERIC_COLUMNS:

        converted = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        invalid_count = converted.isnull().sum()

        if invalid_count > 0:
            invalid_columns[column] = int(
                invalid_count
            )

    return invalid_columns


# ---------------------------------------------------------
# Non-Negative Value Validation
# ---------------------------------------------------------

def validate_non_negative_values(df):
    """
    Check that numerical supply-chain values
    are not negative.
    """

    negative_counts = {}

    for column in NON_NEGATIVE_COLUMNS:

        numeric_values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        negative_count = (
            numeric_values < 0
        ).sum()

        if negative_count > 0:
            negative_counts[column] = int(
                negative_count
            )

    return negative_counts


# ---------------------------------------------------------
# Binary Flag Validation
# ---------------------------------------------------------

def validate_binary_columns(df):
    """
    Check that binary columns contain only 0 or 1.
    """

    invalid_values = {}

    for column in BINARY_COLUMNS:

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        invalid = values[
            ~values.isin([0, 1])
        ]

        if len(invalid) > 0:
            invalid_values[column] = int(
                len(invalid)
            )

    return invalid_values


# ---------------------------------------------------------
# Duplicate Validation
# ---------------------------------------------------------

def validate_duplicates(df):
    """
    Detect duplicate supply-chain records.

    A record is considered a duplicate when it has
    the same Date, SKU, Warehouse and Supplier.
    """

    duplicate_columns = [
        "Date",
        "SKU_ID",
        "Warehouse_ID",
        "Supplier_ID",
    ]

    duplicate_mask = df.duplicated(
        subset=duplicate_columns,
        keep=False,
    )

    duplicate_rows = int(
        duplicate_mask.sum()
    )

    return {
        "duplicate_rows": duplicate_rows,
        "duplicate_groups": int(
            df.loc[
                duplicate_mask,
                duplicate_columns
            ].drop_duplicates().shape[0]
        ),
    }


# ---------------------------------------------------------
# ID Validation
# ---------------------------------------------------------

def validate_ids(df):
    """
    Check that important identifier fields
    are not blank.
    """

    id_columns = [
        "SKU_ID",
        "Warehouse_ID",
        "Supplier_ID",
    ]

    invalid_ids = {}

    for column in id_columns:

        invalid_count = (
            df[column]
            .astype(str)
            .str.strip()
            .isin(["", "nan", "None"])
            .sum()
        )

        if invalid_count > 0:
            invalid_ids[column] = int(
                invalid_count
            )

    return invalid_ids


# ---------------------------------------------------------
# Complete Validation
# ---------------------------------------------------------

def validate_dataset(df):
    """
    Run all validation checks on the dataset.
    """

    results = {
        "valid": True,
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "checks": {},
    }

    # Required columns
    columns_valid, missing_columns = (
        validate_required_columns(df)
    )

    results["checks"]["required_columns"] = {
        "passed": columns_valid,
        "missing_columns": missing_columns,
    }

    if not columns_valid:
        results["valid"] = False

        return results

    # Missing values
    missing_values = validate_missing_values(df)

    results["checks"]["missing_values"] = {
        "passed": len(missing_values) == 0,
        "details": missing_values,
    }

    if missing_values:
        results["valid"] = False

    # Numeric validation
    numeric_errors = validate_numeric_columns(df)

    results["checks"]["numeric_values"] = {
        "passed": len(numeric_errors) == 0,
        "details": numeric_errors,
    }

    if numeric_errors:
        results["valid"] = False

    # Non-negative validation
    negative_values = validate_non_negative_values(df)

    results["checks"]["non_negative_values"] = {
        "passed": len(negative_values) == 0,
        "details": negative_values,
    }

    if negative_values:
        results["valid"] = False

    # Binary validation
    binary_errors = validate_binary_columns(df)

    results["checks"]["binary_flags"] = {
        "passed": len(binary_errors) == 0,
        "details": binary_errors,
    }

    if binary_errors:
        results["valid"] = False

    # Duplicate validation
    duplicates = validate_duplicates(df)

    results["checks"]["duplicates"] = {
        "passed": duplicates["duplicate_rows"] == 0,
        "details": duplicates,
    }

    if duplicates["duplicate_rows"] > 0:
        results["valid"] = False

    # ID validation
    invalid_ids = validate_ids(df)

    results["checks"]["identifiers"] = {
        "passed": len(invalid_ids) == 0,
        "details": invalid_ids,
    }

    if invalid_ids:
        results["valid"] = False

    return results


# ---------------------------------------------------------
# Main Data Pipeline
# ---------------------------------------------------------

def load_and_validate_data(file_path=RAW_DATA_PATH):
    """
    Load and validate the supply-chain dataset.

    Returns:
        df     -> imported pandas DataFrame
        report -> validation report
    """

    df = load_raw_data(file_path)

    report = validate_dataset(df)

    return df, report


# ---------------------------------------------------------
# Standalone Test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("SUPPLY CHAIN DATA IMPORT & VALIDATION")
    print("=" * 60)

    try:

        df, report = load_and_validate_data()

        print(
            f"\nRows Loaded: {report['total_rows']}"
        )

        print(
            f"Columns Loaded: {report['total_columns']}"
        )

        print(
            f"\nOverall Validation: "
            f"{'PASSED' if report['valid'] else 'FAILED'}"
        )

        print("\nValidation Checks:")
        print("-" * 60)

        for check_name, check_result in (
            report["checks"].items()
        ):

            status = (
                "PASSED"
                if check_result["passed"]
                else "FAILED"
            )

            print(
                f"{check_name}: {status}"
            )

            if not check_result["passed"]:
                print(
                    f"  Details: "
                    f"{check_result['details']}"
                )

        print("\n" + "=" * 60)

    except Exception as error:

        print(
            f"\nERROR: {error}"
        )