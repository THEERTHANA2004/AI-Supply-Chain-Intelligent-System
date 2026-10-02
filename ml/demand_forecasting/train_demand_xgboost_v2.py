import pandas as pd
import numpy as np
import joblib
import os

from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 1. LOAD DATA
# ==========================================

DATA_PATH = "data/raw/supply_chain_dataset1.csv"

df = pd.read_csv(DATA_PATH)

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values(
    ["SKU_ID", "Warehouse_ID", "Date"]
).reset_index(drop=True)


# ==========================================
# 2. CREATE HISTORICAL DEMAND FEATURES
# ==========================================

group = df.groupby(
    ["SKU_ID", "Warehouse_ID"]
)["Units_Sold"]


# Previous demand
df["Lag_1"] = group.shift(1)
df["Lag_7"] = group.shift(7)
df["Lag_14"] = group.shift(14)
df["Lag_30"] = group.shift(30)


# Moving averages
df["MA_7"] = group.transform(
    lambda x: x.shift(1).rolling(7).mean()
)

df["MA_14"] = group.transform(
    lambda x: x.shift(1).rolling(14).mean()
)

df["MA_30"] = group.transform(
    lambda x: x.shift(1).rolling(30).mean()
)


# ==========================================
# 3. STRONG COMBINED DEMAND SIGNAL
# ==========================================

df["Combined_MA"] = (
    df["MA_7"] + df["MA_30"]
) / 2


# Demand variability
df["STD_7"] = group.transform(
    lambda x: x.shift(1).rolling(7).std()
)

df["STD_30"] = group.transform(
    lambda x: x.shift(1).rolling(30).std()
)


# ==========================================
# 4. TIME FEATURES
# ==========================================

df["Day"] = df["Date"].dt.day
df["Month"] = df["Date"].dt.month
df["DayOfWeek"] = df["Date"].dt.dayofweek
df["WeekOfYear"] = (
    df["Date"].dt.isocalendar().week.astype(int)
)


# ==========================================
# 5. FEATURES
# ==========================================

features = [
    "Lag_1",
    "Lag_7",
    "Lag_14",
    "Lag_30",
    "MA_7",
    "MA_14",
    "MA_30",
    "Combined_MA",
    "STD_7",
    "STD_30",
    "Day",
    "Month",
    "DayOfWeek",
    "WeekOfYear",
    "Promotion_Flag",
]

target = "Units_Sold"


# ==========================================
# 6. PREPARE MODEL DATA
# ==========================================

df_model = df.dropna(
    subset=features + [target]
).copy()


# ==========================================
# 7. TIME-BASED TRAIN / TEST SPLIT
# ==========================================

split_date = pd.Timestamp("2024-10-01")

train = df_model[
    df_model["Date"] < split_date
]

test = df_model[
    df_model["Date"] >= split_date
]


X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]


print("=" * 60)
print("DEMAND FORECASTING - XGBOOST V3")
print("=" * 60)

print("\nTRAINING DATA")
print("Rows:", len(train))
print(
    "Period:",
    train["Date"].min().date(),
    "to",
    train["Date"].max().date()
)

print("\nTEST DATA")
print("Rows:", len(test))
print(
    "Period:",
    test["Date"].min().date(),
    "to",
    test["Date"].max().date()
)


# ==========================================
# 8. XGBOOST MODEL
# ==========================================

model = XGBRegressor(
    n_estimators=500,
    max_depth=5,
    learning_rate=0.03,
    subsample=0.8,
    colsample_bytree=0.9,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)


# ==========================================
# 9. TRAIN
# ==========================================

print("\nTRAINING MODEL...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# ==========================================
# 10. PREDICT
# ==========================================

predictions = model.predict(X_test)


# ==========================================
# 11. EVALUATE
# ==========================================

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
print("-" * 40)
print(f"MAE : {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R2  : {r2:.4f}")


# ==========================================
# 12. FEATURE IMPORTANCE
# ==========================================

importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(
    ascending=False
)

print("\nTOP FEATURE IMPORTANCE")
print("-" * 40)
print(importance.head(10))


# ==========================================
# 13. SAVE MODEL
# ==========================================

MODEL_DIR = "ml/demand_forecasting/models"

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

MODEL_PATH = (
    f"{MODEL_DIR}/demand_xgboost_v3.pkl"
)

joblib.dump(
    model,
    MODEL_PATH
)

print("\nMODEL SAVED")
print("-" * 40)
print("Location:", MODEL_PATH)

print("\nDONE!")