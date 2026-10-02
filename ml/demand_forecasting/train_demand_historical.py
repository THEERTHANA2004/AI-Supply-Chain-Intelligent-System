import pandas as pd
import numpy as np
import joblib

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor


# Load data
df = pd.read_csv("data/raw/supply_chain_dataset1.csv")
df["Date"] = pd.to_datetime(df["Date"])

# Sort so historical features are calculated correctly
df = df.sort_values(["SKU_ID", "Warehouse_ID", "Date"]).copy()

# Group by SKU + Warehouse
group = df.groupby(["SKU_ID", "Warehouse_ID"])["Units_Sold"]

# Historical demand features
df["Lag_1"] = group.shift(1)
df["Lag_7"] = group.shift(7)
df["Lag_14"] = group.shift(14)
df["Lag_30"] = group.shift(30)

df["MA_7"] = group.transform(
    lambda x: x.shift(1).rolling(7).mean()
)

df["MA_14"] = group.transform(
    lambda x: x.shift(1).rolling(14).mean()
)

df["MA_30"] = group.transform(
    lambda x: x.shift(1).rolling(30).mean()
)

df["STD_7"] = group.transform(
    lambda x: x.shift(1).rolling(7).std()
)

df["STD_30"] = group.transform(
    lambda x: x.shift(1).rolling(30).std()
)

df["Combined_MA"] = (df["MA_7"] + df["MA_30"]) / 2


# Calendar features
df["DayOfWeek"] = df["Date"].dt.dayofweek
df["Month"] = df["Date"].dt.month
df["DayOfMonth"] = df["Date"].dt.day


# Features
features = [
    "Lag_1",
    "Lag_7",
    "Lag_14",
    "Lag_30",
    "MA_7",
    "MA_14",
    "MA_30",
    "STD_7",
    "STD_30",
    "Combined_MA",
    "DayOfWeek",
    "Month",
    "DayOfMonth",
    "Promotion_Flag",
]

target = "Units_Sold"


# Remove rows where historical features are unavailable
df = df.dropna(subset=features).copy()


# Time-based split
train = df[df["Date"] < "2024-10-01"]
test = df[df["Date"] >= "2024-10-01"]

X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]


print("Training rows:", len(train))
print("Testing rows :", len(test))


# XGBoost model
model = XGBRegressor(
    n_estimators=500,
    max_depth=4,
    learning_rate=0.03,
    subsample=0.8,
    colsample_bytree=0.9,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


# Predictions
pred = model.predict(X_test)

# Metrics
mae = mean_absolute_error(y_test, pred)
rmse = np.sqrt(mean_squared_error(y_test, pred))
r2 = r2_score(y_test, pred)

print("\nHISTORICAL DEMAND XGBOOST")
print("-------------------------")
print("MAE :", round(mae, 4))
print("RMSE:", round(rmse, 4))
print("R2  :", round(r2, 4))


# Feature importance
importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print("\nFEATURE IMPORTANCE")
print(importance.round(6))


# Save model
model_path = "ml/demand_forecasting/models/demand_historical_xgboost.pkl"

joblib.dump(model, model_path)

print("\nModel saved to:", model_path)