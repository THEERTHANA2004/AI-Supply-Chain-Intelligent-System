"""
Demand Forecasting Agent

Responsible for:
- Loading historical demand data
- Preparing forecasting features
- Loading the trained forecasting model
- Generating demand forecasts
- Evaluating forecast performance
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class DemandForecastingAgent:
    """AI agent responsible for demand forecasting."""

    def __init__(self):
        self.name = "Demand Forecasting Agent"

        self.data_path = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "raw"
            / "supply_chain_dataset1.csv"
        )

        self.model_path = (
            Path(__file__).resolve().parents[2]
            / "ml"
            / "demand_forecasting"
            / "models"
            / "demand_historical_xgboost.pkl"
        )

    def load_data(self):
        """Load the supply-chain dataset."""

        df = pd.read_csv(self.data_path)
        df["Date"] = pd.to_datetime(df["Date"])

        return df

    def prepare_features(self, df):
        """Create historical demand features."""

        df = df.sort_values(
            ["SKU_ID", "Warehouse_ID", "Date"]
        ).copy()

        group = df.groupby(
            ["SKU_ID", "Warehouse_ID"]
        )["Units_Sold"]

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

        df["Combined_MA"] = (
            df["MA_7"] + df["MA_30"]
        ) / 2

        df["DayOfWeek"] = df["Date"].dt.dayofweek
        df["Month"] = df["Date"].dt.month
        df["DayOfMonth"] = df["Date"].dt.day

        return df

    def load_model(self):
        """Load the trained demand forecasting model."""

        return joblib.load(self.model_path)

    def predict(self, df):
        """Generate demand predictions."""

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

        model = self.load_model()

        valid_data = df.dropna(
            subset=features
        ).copy()

        valid_data["Predicted_Demand"] = model.predict(
            valid_data[features]
        )

        return valid_data

    def evaluate(self, predictions):
        """Evaluate forecast performance."""

        actual = predictions["Units_Sold"]
        predicted = predictions["Predicted_Demand"]

        mae = mean_absolute_error(
            actual,
            predicted
        )

        rmse = mean_squared_error(
            actual,
            predicted
        ) ** 0.5

        r2 = r2_score(
            actual,
            predicted
        )

        if mae <= 3:
            quality = "High"
        elif mae <= 5:
            quality = "Moderate"
        else:
            quality = "Needs Improvement"

        return {
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2,
            "Forecast_Quality": quality,
        }


if __name__ == "__main__":
    agent = DemandForecastingAgent()

    data = agent.load_data()
    data = agent.prepare_features(data)

    model = agent.load_model()

    predictions = agent.predict(data)

    evaluation = agent.evaluate(predictions)

    print("Agent:", agent.name)
    print("Rows:", len(data))
    print("Columns:", len(data.columns))
    print("Model loaded:", type(model).__name__)

    print("\nPrediction rows:", len(predictions))

    print("\nModel Evaluation:")

    print(f"MAE: {evaluation['MAE']:.4f}")
    print(f"RMSE: {evaluation['RMSE']:.4f}")
    print(f"R2: {evaluation['R2']:.4f}")
    print(f"Forecast Quality: {evaluation['Forecast_Quality']}")

    print("\nSample Predictions:")

    print(
        predictions[
            [
                "Date",
                "SKU_ID",
                "Warehouse_ID",
                "Units_Sold",
                "Predicted_Demand",
            ]
        ].tail(5).to_string(index=False)
    )