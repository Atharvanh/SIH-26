import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from sqlalchemy import func, distinct
from app.db import SessionLocal
from app.models.mandi_price import MandiPriceHistory
from app.services.sale_window_service import recommend_sale_window

MIN_DISTINCT_DATES = 300

def find_wait_examples():
    session = SessionLocal()
    results = []
    
    try:
        print("Querying database for valid market combinations...")
        valid_markets = (
            session.query(
                MandiPriceHistory.state,
                MandiPriceHistory.commodity,
                MandiPriceHistory.market,
                func.count(distinct(MandiPriceHistory.price_date))
            )
            .group_by(MandiPriceHistory.state, MandiPriceHistory.commodity, MandiPriceHistory.market)
            .having(func.count(distinct(MandiPriceHistory.price_date)) >= MIN_DISTINCT_DATES)
            .all()
        )
        
        print(f"Found {len(valid_markets)} valid combinations with >= {MIN_DISTINCT_DATES} dates.")
        print("Running forecasting and sale window logic for all valid markets (this may take a minute)...")
        
        for state, commodity, market, count in valid_markets:
            try:
                res = recommend_sale_window(state, commodity, market, forecast_days=7)
                if "error" not in res:
                    results.append({
                        "state": state,
                        "commodity": commodity,
                        "market": market,
                        "decision": res.get("decision", "SELL_NOW"),
                        "net_benefit_pct": res.get("net_benefit_pct", -999.0),
                        "recommended_date": res.get("recommended_date", "today"),
                        "days_to_peak": res.get("days_to_peak", 0),
                        "backtested_mape": res.get("backtested_mape", 0.0) or 0.0,
                        "signal_confidence": res.get("signal_confidence", "LOW")
                    })
            except Exception as e:
                pass
                
        # Sort results by net_benefit_pct descending
        results.sort(key=lambda x: x["net_benefit_pct"], reverse=True)
        
        wait_results = [r for r in results if r["decision"] == "WAIT"]
        
        if wait_results:
            print("\n=======================================================================================================================")
            print("WAIT EXAMPLES FOUND")
            print("=======================================================================================================================")
            print(f"{'State':<18} {'Commodity':<20} {'Market':<25} {'Decision':<10} {'Net Ben%':>8} {'MAPE%':>7} {'Conf':<6} {'Rec Date':>12} {'Days':>4}")
            print("-" * 119)
            for r in wait_results:
                print(f"{r['state']:<18} {r['commodity']:<20} {r['market']:<25} {r['decision']:<10} {r['net_benefit_pct']:>8.2f} {r['backtested_mape']:>7.2f} {r['signal_confidence']:<6} {r['recommended_date']:>12} {r['days_to_peak']:>4}")
            print("=======================================================================================================================")
        else:
            print("\nNO WAIT EXAMPLES FOUND.")
            print("\nTop 5 Closest to WAIT (Highest net_benefit_pct):")
            print(f"{'State':<18} {'Commodity':<20} {'Market':<25} {'Decision':<10} {'Net Ben%':>8} {'MAPE%':>7} {'Conf':<6} {'Rec Date':>12} {'Days':>4}")
            print("-" * 119)
            for r in results[:5]:
                print(f"{r['state']:<18} {r['commodity']:<20} {r['market']:<25} {r['decision']:<10} {r['net_benefit_pct']:>8.2f} {r['backtested_mape']:>7.2f} {r['signal_confidence']:<6} {r['recommended_date']:>12} {r['days_to_peak']:>4}")
                
    finally:
        session.close()

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    find_wait_examples()
