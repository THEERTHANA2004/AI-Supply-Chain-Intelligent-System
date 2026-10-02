import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# 1. LOAD DATASET
# ============================================================

DATA_PATH = Path("data/raw/supply_chain_dataset1.csv")

df = pd.read_csv(DATA_PATH)

print("=" * 70)
print("AI DEMAND FORECASTING MODEL")
print("=" * 70)

print(f"\nOriginal dataset shape: {df.shape}")


# ============================================================
# 2. DATE PROCESSING
# ============================================================

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values(
    ["SKU_ID", "Warehouse_ID", "Date"]
).reset_index(drop=True)

print(
    f"Date range: "
    f"{df['Date'].min().date()} to "
    f"{df['Date'].max().date()}"
)


# ============================================================
# 3. TIME FEATURES
# ============================================================

df["Day"] = df["Date"].dt.day
df["Month"] = df["Date"].dt.month
df["DayOfWeek"] = df["Date"].dt.dayofweek
df["WeekOfYear"] = df["Date"].dt.isocalendar().week.astype(int)


# ============================================================
# 4. DEMAND LAG FEATURES
# ============================================================

group_cols = ["SKU_ID", "Warehouse_ID"]

df["Demand_Lag_1"] = (
    df.groupby(group_cols)["Units_Sold"]
    .shift(1)
)

df["Demand_Lag_7"] = (
    df.groupby(group_cols)["Units_Sold"]
    .shift(7)
)

df["Demand_Lag_30"] = (
    df.groupby(group_cols)["Units_Sold"]
    .shift(30)
)


# ============================================================
# 5. ROLLING DEMAND FEATURES
# ============================================================

df["Demand_Rolling_7"] = (
    df.groupby(group_cols)["Units_Sold"]
    .transform(
        lambda x: x.shift(1).rolling(7).mean()
    )
)

df["Demand_Rolling_30"] = (
    df.groupby(group_cols)["Units_Sold"]
    .transform(
        lambda x: x.shift(1).rolling(30).mean()
    )
)


# ============================================================
# 6. REMOVE UNAVAILABLE HISTORY
# ============================================================

df = df.dropna().reset_index(drop=True)

print(f"\nPrepared dataset shape: {df.shape}")


# ============================================================
# 7. SELECT MODEL FEATURES
# ============================================================

features = [
    "Day",
    "Month",
    "DayOfWeek",
    "WeekOfYear",
    "Demand_Lag_1",
    "Demand_Lag_7",
    "Demand_Lag_30",
    "Demand_Rolling_7",
    "Demand_Rolling_30",
    "Inventory_Level",
    "Supplier_Lead_Time_Days",
    "Reorder_Point",
    "Order_Quantity",
    "Unit_Cost",
    "Unit_Price",
    "Promotion_Flag",
]

target = "Units_Sold"


# ============================================================
# 8. TIME-BASED TRAIN / TEST SPLIT
# ============================================================

# IMPORTANT:
# We split by time instead of randomly mixing future and past data.

split_date = pd.Timestamp("2024-10-01")

train_df = df[df["Date"] < split_date].copy()
test_df = df[df["Date"] >= split_date].copy()

print("\nTIME-BASED SPLIT")
print("-" * 70)
print(f"Training rows: {len(train_df)}")
print(f"Testing rows:  {len(test_df)}")

print(
    f"Training period: "
    f"{train_df['Date'].min().date()} to "
    f"{train_df['Date'].max().date()}"
)

print(
    f"Testing period:  "
    f"{test_df['Date'].min().date()} to "
    f"{test_df['Date'].max().date()}"
)


# ============================================================
# 9. CREATE X AND Y
# ============================================================

X_train = train_df[features]
y_train = train_df[target]

X_test = test_df[features]
y_test = test_df[target]


# ============================================================
# 10. CREATE XGBOOST MODEL
# ============================================================

print("\nTraining XGBoost model...")

model = XGBRegressor(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)


# ============================================================
# 11. TRAIN MODEL
# ============================================================

model.fit(
    X_train,
    y_train
)

print("Model training completed.")


# ============================================================
# 12. MAKE PREDICTIONS
# ============================================================

predictions = model.predict(X_test)


# ============================================================
# 13. EVALUATE MODEL
# ============================================================

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)


print("\nMODEL PERFORMANCE")
print("-" * 70)

print(f"MAE :  {mae:.4f}")
print(f"RMSE:  {rmse:.4f}")
print(f"R²  :  {r2:.4f}")


# ============================================================
# 14. SAVE MODEL
# ============================================================

MODEL_DIR = Path("ml/demand_forecasting/models")

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_PATH = MODEL_DIR / "demand_xgboost_model.pkl"

joblib.dump(
    model,
    MODEL_PATH
)

print("\nMODEL SAVED")
print("-" * 70)
print(f"Location: {MODEL_PATH}")


# ============================================================
# 15. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

print("\nTOP FEATURE IMPORTANCE")
print("-" * 70)

print(
    importance.head(10).to_string(
        index=False
    )
)


# ============================================================
# 16. COMPLETION
# ============================================================

print("\n" + "=" * 70)
print("DEMAND FORECASTING MODEL COMPLETED")
print("=" * 70)