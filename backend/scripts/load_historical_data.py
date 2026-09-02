import os
import sys
import time
from datetime import datetime

# Add the backend directory to the Python path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pandas as pd
from sqlalchemy import func
from app.db import init_db, SessionLocal
from app.models.mandi_price import MandiPriceHistory

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "historical_prices.csv")
CHUNK_SIZE = 50000

# Column mapping from CSV headers to model fields
COLUMN_MAP = {
    "State": "state",
    "District Name": "district",
    "Market Name": "market",
    "Commodity": "commodity",
    "Variety": "variety",
    "Grade": "grade",
    "Min Price (Rs./Quintal)": "min_price",
    "Max Price (Rs./Quintal)": "max_price",
    "Modal Price (Rs./Quintal)": "modal_price",
    "Price Date": "price_date",
}


def parse_price_date(date_str):
    """Parse date strings like '05 Apr 2025' into a date object."""
    try:
        return datetime.strptime(str(date_str).strip(), "%d %b %Y").date()
    except (ValueError, TypeError):
        return None


def load_historical_data():
    print("=" * 60)
    print("HISTORICAL MANDI PRICE DATA LOADER")
    print("=" * 60)

    # Initialize database and tables
    init_db()

    total_inserted = 0
    total_skipped = 0
    chunk_num = 0
    start_time = time.time()

    print(f"\nReading CSV: {CSV_PATH}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print("-" * 60)

    session = SessionLocal()

    try:
        for chunk in pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE):
            chunk_num += 1

            # Rename columns to match model fields
            chunk = chunk.rename(columns=COLUMN_MAP)

            # Keep only the columns we need
            keep_cols = list(COLUMN_MAP.values())
            chunk = chunk[[c for c in keep_cols if c in chunk.columns]]

            # Parse price_date
            chunk["price_date"] = chunk["price_date"].apply(parse_price_date)

            # Drop rows with missing price_date or missing modal_price
            before_count = len(chunk)
            chunk = chunk.dropna(subset=["price_date", "modal_price"])
            dropped = before_count - len(chunk)
            total_skipped += dropped

            # Convert to list of dicts for bulk insert
            records = chunk.to_dict(orient="records")

            # Bulk insert
            session.bulk_insert_mappings(MandiPriceHistory, records)
            session.commit()

            total_inserted += len(records)
            elapsed = time.time() - start_time
            print(f"  Chunk {chunk_num}: inserted {len(records)}, skipped {dropped}, "
                  f"total so far: {total_inserted} ({elapsed:.1f}s)")

        # Final summary
        print("\n" + "=" * 60)
        print("LOAD COMPLETE")
        print("=" * 60)

        # Query summary stats from the database
        min_date = session.query(func.min(MandiPriceHistory.price_date)).scalar()
        max_date = session.query(func.max(MandiPriceHistory.price_date)).scalar()
        distinct_states = session.query(func.count(func.distinct(MandiPriceHistory.state))).scalar()
        distinct_commodities = session.query(func.count(func.distinct(MandiPriceHistory.commodity))).scalar()

        elapsed = time.time() - start_time
        print(f"  Total rows inserted:    {total_inserted}")
        print(f"  Total rows skipped:     {total_skipped}")
        print(f"  Min price_date in DB:   {min_date}")
        print(f"  Max price_date in DB:   {max_date}")
        print(f"  Distinct states:        {distinct_states}")
        print(f"  Distinct commodities:   {distinct_commodities}")
        print(f"  Time elapsed:           {elapsed:.1f}s")
        print("=" * 60)

    except Exception as e:
        session.rollback()
        print(f"\nERROR: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    load_historical_data()
