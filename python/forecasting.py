import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine

db_password = os.getenv("STOCKSIGHT_DB_PASSWORD")
if not db_password:
    raise ValueError("Set the STOCKSIGHT_DB_PASSWORD environment variable first.")

engine = create_engine(
    f"postgresql+psycopg://postgres:{db_password}@localhost:5432/StockSight"
)

output_dir = Path(__file__).resolve().parent
output_dir.mkdir(parents=True, exist_ok=True)

query = """
SELECT sale_date, SUM(quantity) AS units_sold
FROM analytics.sales
GROUP BY sale_date
ORDER BY sale_date;
"""

try:
    df = pd.read_sql(query, engine)
finally:
    engine.dispose()

df["sale_date"] = pd.to_datetime(df["sale_date"])
df["units_sold"] = pd.to_numeric(df["units_sold"], errors="raise")
df = df.sort_values("sale_date").reset_index(drop=True)

if df.empty or len(df) < 7 + 90:
    raise ValueError("Not enough daily sales data for forecasting.")

print("Connected to PostgreSQL!")
print("\nSales data loaded!")
print(df.head())
print("\nNumber of days:", len(df))

test_window = 90
train = df.iloc[:-test_window].copy()
test = df.iloc[-test_window:].copy()

print("\nTraining days:", len(train))
print("Testing days:", len(test))
print("\nTraining period:")
print(train["sale_date"].min(), "to", train["sale_date"].max())
print("\nTesting period:")
print(test["sale_date"].min(), "to", test["sale_date"].max())


def recursive_smoothing_forecast(training_values, forecast_days):
    history = [float(value) for value in training_values]
    predictions = []
    for _ in range(forecast_days):
        recent = sum(history[-7:]) / min(7, len(history))
        same_weekday = history[-7]
        prediction = max(0, 0.70 * recent + 0.30 * same_weekday)
        predictions.append(prediction)
        history.append(prediction)
    return predictions


def weekly_seasonal_forecast(training_values, forecast_days):
    """Repeat the last observed 7-day pattern without using test actuals."""
    values = [float(value) for value in training_values]
    if len(values) < 7:
        raise ValueError("At least 7 training days are required.")
    return [max(0, values[-7 + (i % 7)]) for i in range(forecast_days)]


def level_forecast(training_values, forecast_days):
    values = pd.Series(training_values, dtype=float)
    level = float(values.tail(28).mean())
    return [max(0, level)] * forecast_days


def evaluate_forecast(actual, predicted):
    actual = pd.Series(actual, dtype=float).reset_index(drop=True)
    predicted = pd.Series(predicted, dtype=float).reset_index(drop=True)
    errors = actual - predicted
    mae = errors.abs().mean()
    rmse = (errors.pow(2).mean()) ** 0.5
    total_actual = actual.sum()
    wape = errors.abs().sum() / total_actual * 100 if total_actual else float("nan")
    return mae, rmse, wape


test["current_model_forecast"] = recursive_smoothing_forecast(
    train["units_sold"], len(test)
)
test["baseline_forecast"] = level_forecast(train["units_sold"], len(test))
test["seasonal_forecast"] = weekly_seasonal_forecast(
    train["units_sold"], len(test)
)

model_columns = {
    "Current Model": "current_model_forecast",
    "28-Day Mean Baseline": "baseline_forecast",
    "Weekly Seasonal": "seasonal_forecast",
}

print("\nForecast Model Comparison")
print("-------------------------")
print(f"{'Method':<24}{'MAE':>12}{'RMSE':>12}{'WAPE':>12}")
print("-" * 60)

metrics_by_model = {}
for name, column in model_columns.items():
    metrics = evaluate_forecast(test["units_sold"], test[column])
    metrics_by_model[name] = metrics
    mae, rmse, wape = metrics
    print(f"{name:<24}{mae:>12.2f}{rmse:>12.2f}{wape:>11.2f}%")

best_model_name = min(metrics_by_model, key=lambda name: metrics_by_model[name][2])
best_column = model_columns[best_model_name]
test["forecast"] = test[best_column]
print(f"\nSelected forecast for export/chart: {best_model_name} (lowest test WAPE).")
print("\nFirst 10 Forecast Results")
print(test[["sale_date", "units_sold", "forecast"]].head(10).to_string(index=False))

plt.figure(figsize=(14, 6))
plt.plot(test["sale_date"], test["units_sold"], label="Actual Demand", linewidth=1.8)
plt.plot(test["sale_date"], test["forecast"], label=f"Selected Forecast: {best_model_name}", linewidth=2)
plt.title("StockSight: Actual vs Forecast Demand (90-Day Test Period)")
plt.xlabel("Date")
plt.ylabel("Units Sold")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
chart_path = output_dir / "forecast_comparison.png"
plt.savefig(chart_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"\nForecast chart saved to: {chart_path}")

forecast_output = test[
    ["sale_date", "units_sold", "forecast", "current_model_forecast",
     "baseline_forecast", "seasonal_forecast"]
].copy()
csv_path = output_dir / "forecast_results.csv"
forecast_output.to_csv(csv_path, index=False)
print(f"Forecast CSV saved to: {csv_path}")
print(f"Exported rows: {len(forecast_output)}")

print("\nMultiple-Period Backtesting")
print("---------------------------")
number_of_periods = 4
backtest_results = []

for period in range(number_of_periods, 0, -1):
    test_end = len(df) - (period - 1) * test_window
    test_start = test_end - test_window
    if test_start < 7:
        continue

    training_data = df.iloc[:test_start]["units_sold"].astype(float)
    testing_data = df.iloc[test_start:test_end]["units_sold"].astype(float)

    candidates = {
        "Current Model": recursive_smoothing_forecast(training_data, len(testing_data)),
        "28-Day Mean Baseline": level_forecast(training_data, len(testing_data)),
        "Weekly Seasonal": weekly_seasonal_forecast(training_data, len(testing_data)),
    }
    period_metrics = {
        name: evaluate_forecast(testing_data, preds)
        for name, preds in candidates.items()
    }
    chosen_name = min(period_metrics, key=lambda name: period_metrics[name][2])
    mae, rmse, wape = period_metrics[chosen_name]
    backtest_results.append({
        "Test Start": df.iloc[test_start]["sale_date"].date(),
        "Test End": df.iloc[test_end - 1]["sale_date"].date(),
        "Selected Model": chosen_name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "WAPE (%)": round(wape, 2),
    })

backtest_df = pd.DataFrame(backtest_results)
print(backtest_df.to_string(index=False))
backtest_path = output_dir / "backtest_results.csv"
backtest_df.to_csv(backtest_path, index=False)
print(f"\nBacktest results saved to: {backtest_path}")
