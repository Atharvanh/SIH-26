import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.data.simulated_buyers import BUYERS
from app.services.distance_service import estimate_road_distance_km
from app.services.net_realization_service import calculate_net_realization

def test():
    # Aralamoodu, Kerala's approx coords
    farmer_lat = 8.3912
    farmer_lon = 77.0620
    quantity_quintals = 10
    commodity = "Cabbage"

    print(f"Testing Net Realization for {commodity} (Quantity: {quantity_quintals} quintals)")
    print(f"Farmer Location (Aralamoodu): Lat {farmer_lat}, Lon {farmer_lon}")
    print("-" * 80)

    cabbage_buyers = [b for b in BUYERS if commodity in b["commodities_bought"]][:3]

    if not cabbage_buyers:
        print("No buyers found for Cabbage!")
        return

    for buyer in cabbage_buyers:
        print(f"Buyer: {buyer['name']} ({buyer['buyer_type']}) - ID: {buyer['buyer_id']}")
        
        distance = estimate_road_distance_km(
            farmer_lat, farmer_lon, 
            buyer['latitude'], buyer['longitude']
        )
        
        print(f"  Distance: {distance:.2f} km")
        print(f"  Offered Price: Rs.{buyer['offered_price_per_quintal']} / quintal")
        print(f"  Reliability: {buyer['on_time_payment_pct']}% on-time payment")

        breakdown = calculate_net_realization(
            offered_price=buyer['offered_price_per_quintal'],
            quantity_quintals=quantity_quintals,
            distance_km=distance,
            buyer_on_time_payment_pct=buyer['on_time_payment_pct']
        )

        print("  --- Breakdown ---")
        print(f"  Gross Revenue          : Rs.{breakdown['gross_revenue']:>8.2f}")
        print(f"  - Transport Cost       : Rs.{breakdown['transport_cost']:>8.2f}")
        print(f"  - Commission (6%)      : Rs.{breakdown['commission_cost']:>8.2f}")
        print(f"  - Reliability Adj ({breakdown['reliability_discount_pct']}%) : Rs.{breakdown['reliability_adjustment']:>8.2f}")
        print("  -------------------")
        print(f"  Net Realization        : Rs.{breakdown['net_realization']:>8.2f}")
        print(f"  Net Realization/Qtl    : Rs.{breakdown['net_realization_per_quintal']:>8.2f}")
        print("-" * 80)

if __name__ == "__main__":
    test()
