import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Locate the dataset
# --------------------------------------------------

dataset_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "supply_chain_dataset1.csv"
# --------------------------------------------------
# 2. Load the dataset
# --------------------------------------------------

df = pd.read_csv(dataset_path)

# --------------------------------------------------
# 3. Basic dataset information
# --------------------------------------------------

print("=" * 60)
print("SUPPLY CHAIN DATASET INSPECTION")
print("=" * 60)

print("\n1. DATASET SHAPE")
print("-" * 60)
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\n2. COLUMN NAMES")
print("-" * 60)
for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")

print("\n3. DATA TYPES")
print("-" * 60)
print(df.dtypes)

print("\n4. MISSING VALUES")
print("-" * 60)
missing_values = df.isnull().sum()
print(missing_values)

print("\n5. DUPLICATE ROWS")
print("-" * 60)
print("Duplicate rows:", df.duplicated().sum())

print("\n6. FIRST 5 ROWS")
print("-" * 60)
print(df.head())

print("\n7. NUMERICAL SUMMARY")
print("-" * 60)
print(df.describe())

print("\n" + "=" * 60)
print("INSPECTION COMPLETED")
print("=" * 60)