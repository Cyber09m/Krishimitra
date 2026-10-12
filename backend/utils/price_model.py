"""
Crop price prediction.

Honest scope: this is a linear-trend regression over recent historical
mandi prices per crop, not a deep time-series model. It's deliberately kept
simple and explainable — a farmer-facing number should come with a
confidence range, not false precision. The house style here is: correct
and legible over impressively-named-but-opaque.
"""
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crop_prices_sample.csv")
_df_cache = None


def _load_data():
    global _df_cache
    if _df_cache is None:
        _df_cache = pd.read_csv(CSV_PATH, parse_dates=["date"])
    return _df_cache


def get_history(crop: str, market: str = None):
    df = _load_data()
    subset = df[df["crop"].str.lower() == crop.lower()]
    if market:
        subset = subset[subset["market"].str.lower() == market.lower()]
    subset = subset.sort_values("date")
    return subset[["date", "market", "price_per_quintal"]].to_dict(orient="records")


def predict_price(crop: str, days_ahead: int = 7, market: str = None):
    df = _load_data()
    subset = df[df["crop"].str.lower() == crop.lower()]
    if market:
        subset = subset[subset["market"].str.lower() == market.lower()]

    if subset.empty:
        return None

    subset = subset.sort_values("date").reset_index(drop=True)
    subset["day_index"] = np.arange(len(subset))

    X = subset[["day_index"]].values
    y = subset["price_per_quintal"].values

    model = LinearRegression()
    model.fit(X, y)

    last_index = subset["day_index"].max()
    future_index = last_index + days_ahead
    predicted = float(model.predict([[future_index]])[0])

    # Simple confidence band from residual std-dev — communicates "this is
    # an estimate, not a guarantee" rather than a bare point number.
    residuals = y - model.predict(X)
    residual_std = float(np.std(residuals))

    last_known_price = float(subset.iloc[-1]["price_per_quintal"])
    last_known_date = subset.iloc[-1]["date"].strftime("%Y-%m-%d")

    return {
        "crop": crop,
        "market": market or "all markets (averaged)",
        "last_known_price": round(last_known_price, 2),
        "last_known_date": last_known_date,
        "predicted_price": round(predicted, 2),
        "predicted_for_days_ahead": days_ahead,
        "confidence_range": {
            "low": round(predicted - residual_std, 2),
            "high": round(predicted + residual_std, 2),
        },
        "trend": "rising" if model.coef_[0] > 0 else "falling",
        "disclaimer": (
            "This is a linear-trend estimate based on recent historical mandi "
            "prices, not a guaranteed price. Use it as directional guidance "
            "alongside local market checks before making a selling decision."
        ),
    }
