import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pandas as pd
import numpy as np
from sqlalchemy import func, distinct
from app.db import SessionLocal
from app.models.mandi_price import MandiPriceHistory

MIN_DISTINCT_DATES = 300
COMMODITIES = ["Green Chilli", "Brinjal"]

def find_volatile_markets():
    session = SessionLocal()
    results = []

    try:
        # Get all distinct states
        states = [r[0] for r in session.query(distinct(MandiPriceHistory.state)).all()]

        for commodity in COMMODITIES:
            for state in states:
                # Find all markets for this state+commodity with date counts
                market_rows = (
                    session.query(
                        MandiPriceHistory.market,
                        func.count(distinct(MandiPriceHistory.price_date)),
                    )
                    .filter(
                        MandiPriceHistory.state == state,
                        MandiPriceHistory.commodity == commodity,
                    )
                    .group_by(MandiPriceHistory.market)
                    .having(func.count(distinct(MandiPriceHistory.price_date)) >= MIN_DISTINCT_DATES)
                    .all()
                )

                for market_name, date_count in market_rows:
                    # Get all modal_price values for this combo
                    prices = [
                        r[0] for r in
                        session.query(MandiPriceHistory.modal_price)
                        .filter(
                            MandiPriceHistory.state == state,
                            MandiPriceHistory.commodity == commodity,
                            MandiPriceHistory.market == market_name,
                            MandiPriceHistory.modal_price.isnot(None),
                        )
                        .all()
                    ]

                    if len(prices) < 10:
                        continue

                    arr = np.array(prices, dtype=float)
                    mean_price = np.mean(arr)
                    std_price = np.std(arr)
                    min_price = np.min(arr)
                    max_price = np.max(arr)

                    if mean_price == 0:
                        continue

                    cv = std_price / mean_price

                    results.append({
                        "state": state,
                        "commodity": commodity,
                        "market": market_name,
                        "distinct_dates": date_count,
                        "mean_price": round(mean_price, 1),
                        "std_price": round(std_price, 1),
                        "min_price": round(min_price, 1),
                        "max_price": round(max_price, 1),
                        "cv": round(cv, 4),
                    })

        # Sort by CV descending
        results.sort(key=lambda x: x["cv"], reverse=True)

        # Print top 10
        print("=" * 110)
        print("TOP 10 MOST VOLATILE MARKETS (min 300 distinct dates)")
        print("=" * 110)
        print(f"{'Rank':<5} {'State':<18} {'Commodity':<15} {'Market':<25} {'Dates':<7} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8} {'CV':>8}")
        print("-" * 110)
        for i, r in enumerate(results[:10], 1):
            print(f"{i:<5} {r['state']:<18} {r['commodity']:<15} {r['market']:<25} {r['distinct_dates']:<7} {r['mean_price']:>8.1f} {r['std_price']:>8.1f} {r['min_price']:>8.1f} {r['max_price']:>8.1f} {r['cv']:>8.4f}")
        print("=" * 110)
        print(f"\nTotal qualifying markets found: {len(results)}")

        if results:
            best = results[0]
            print(f"\nBest pick: state={best['state']}, commodity={best['commodity']}, market={best['market']}")
            print(f"  CV={best['cv']}, {best['distinct_dates']} dates, price range {best['min_price']}-{best['max_price']}")

    finally:
        session.close()


if __name__ == "__main__":
    find_volatile_markets()
