import logging
import warnings
import pandas as pd
import numpy as np
from datetime import timedelta
from sqlalchemy import func
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from app.db import SessionLocal
from app.models.mandi_price import MandiPriceHistory

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def get_price_series(state, commodity, market):
    """
    Query MandiPriceHistory and return a pandas Series of modal_price
    indexed by price_date, sorted chronologically.
    """
    session = SessionLocal()
    try:
        rows = (
            session.query(MandiPriceHistory.price_date, MandiPriceHistory.modal_price)
            .filter(
                MandiPriceHistory.state == state,
                MandiPriceHistory.commodity == commodity,
                MandiPriceHistory.market == market,
            )
            .order_by(MandiPriceHistory.price_date)
            .all()
        )

        if not rows:
            return None

        df = pd.DataFrame(rows, columns=["price_date", "modal_price"])
        # If multiple entries per day (different varieties), average them
        df = df.groupby("price_date")["modal_price"].mean()
        df.index = pd.DatetimeIndex(df.index)
        df = df.sort_index()
        return df

    finally:
        session.close()


def prepare_series(series):
    """
    Resample to daily frequency, forward-fill gaps up to 3 days,
    and validate completeness.
    Returns (prepared_series, None) on success or (None, reason_string) on failure.
    """
    if series is None or len(series) < 14:
        return None, "Not enough data points (need at least 14 days)"

    # Resample to daily frequency
    daily = series.asfreq("D")

    # Forward-fill gaps up to 3 consecutive days
    daily = daily.ffill(limit=3)

    # Check how many are still missing
    total_days = len(daily)
    missing = daily.isna().sum()
    missing_pct = missing / total_days

    if missing_pct > 0.10:
        return None, f"Too many missing values after fill: {missing}/{total_days} ({missing_pct:.1%})"

    # Drop any remaining NaN rows at the edges
    daily = daily.dropna()

    if len(daily) < 14:
        return None, f"Not enough data after cleaning: {len(daily)} days"

    return daily, None


def train_and_forecast(series, forecast_days=7):
    """
    Train Holt-Winters model, backtest on last 14 days, forecast into the future.
    Returns dict with forecast, mape, and recent history.
    """
    test_size = 14

    if len(series) <= test_size + 7:
        return None, "Not enough data for train/test split"

    train = series[:-test_size]
    test = series[-test_size:]

    # Decide on seasonality: need at least 2 full seasonal cycles (14 days for weekly)
    seasonal = None
    seasonal_periods = None
    if len(train) >= 14:
        seasonal = "add"
        seasonal_periods = 7

    # Fit on train set for backtesting
    try:
        model_train = ExponentialSmoothing(
            train,
            trend="add",
            seasonal=seasonal,
            seasonal_periods=seasonal_periods,
            initialization_method="estimated",
        ).fit(optimized=True)

        test_pred = model_train.forecast(test_size)

        # Compute MAPE on backtest
        actual = test.values
        predicted = test_pred.values
        # Avoid division by zero
        mask = actual != 0
        if mask.sum() > 0:
            mape = float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)
        else:
            mape = None

    except Exception as e:
        logger.warning(f"Backtest model failed: {e}, trying without seasonality")
        # Fallback: no seasonality
        try:
            model_train = ExponentialSmoothing(
                train,
                trend="add",
                seasonal=None,
                initialization_method="estimated",
            ).fit(optimized=True)

            test_pred = model_train.forecast(test_size)
            actual = test.values
            predicted = test_pred.values
            mask = actual != 0
            if mask.sum() > 0:
                mape = float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)
            else:
                mape = None
            seasonal = None
            seasonal_periods = None

        except Exception as e2:
            logger.error(f"Fallback model also failed: {e2}")
            return None, f"Model training failed: {e2}"

    # Refit on FULL series and forecast into the future
    try:
        model_full = ExponentialSmoothing(
            series,
            trend="add",
            seasonal=seasonal,
            seasonal_periods=seasonal_periods,
            initialization_method="estimated",
        ).fit(optimized=True)

        future_pred = model_full.forecast(forecast_days)

    except Exception as e:
        # Fallback without seasonality for final model
        try:
            model_full = ExponentialSmoothing(
                series,
                trend="add",
                seasonal=None,
                initialization_method="estimated",
            ).fit(optimized=True)
            future_pred = model_full.forecast(forecast_days)
        except Exception as e2:
            return None, f"Final model training failed: {e2}"

    # Build forecast list
    forecast = []
    for dt, val in future_pred.items():
        forecast.append({
            "date": dt.strftime("%Y-%m-%d"),
            "predicted_price": round(float(val), 2),
        })

    # Last 30 days of actual historical prices
    last_30 = series[-30:]
    historical = []
    for dt, val in last_30.items():
        historical.append({
            "date": dt.strftime("%Y-%m-%d"),
            "price": round(float(val), 2),
        })

    return {
        "historical": historical,
        "forecast": forecast,
        "backtested_mape": round(mape, 2) if mape is not None else None,
    }, None


def naive_baseline_mape(series, test_size=14):
    """
    Compute MAPE for a naive persistence baseline: predict each test day's
    price as the actual price from exactly 1 day before it.
    Uses the same train/test split as train_and_forecast.
    """
    if len(series) <= test_size + 1:
        return None

    test = series[-test_size:]

    # For each test day, the naive prediction is the actual value from the day before
    # The day before the first test day is the last training day
    naive_preds = series[-(test_size + 1):-1].values
    actual = test.values

    mask = actual != 0
    if mask.sum() == 0:
        return None

    mape = float(np.mean(np.abs((actual[mask] - naive_preds[mask]) / actual[mask])) * 100)
    return round(mape, 2)


def check_fill_ratio(raw_series, prepared_series, test_days=14):
    """
    For the last `test_days` of the prepared series, report how many values
    were real observations vs forward-filled.
    """
    if prepared_series is None or len(prepared_series) < test_days:
        return None

    # Get the last test_days dates from the prepared series
    test_dates = prepared_series.index[-test_days:]

    # The raw_series index has the actual observed dates
    raw_dates = set(raw_series.index)

    real_count = 0
    filled_count = 0
    for dt in test_dates:
        if dt in raw_dates:
            real_count += 1
        else:
            filled_count += 1

    return {
        "test_days": test_days,
        "real_observations": real_count,
        "forward_filled": filled_count,
        "description": f"{filled_count} of {test_days} days were forward-filled, {real_count} were real observations",
    }
