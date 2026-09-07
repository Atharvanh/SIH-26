import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.data.simulated_buyers import BUYERS
from app.services.distance_service import estimate_road_distance_km
from app.services.net_realization_service import calculate_net_realization


def check_ranking_flip():
    farmer_lat = 8.3912
    farmer_lon = 77.0620
    quantity = 10
    commodity = "Cabbage"

    cabbage_buyers = [b for b in BUYERS if commodity in b["commodities_bought"]]

    if not cabbage_buyers:
        print("No buyers found for Cabbage!")
        return

    # Calculate net realization for each buyer
    enriched = []
    for b in cabbage_buyers:
        dist = estimate_road_distance_km(farmer_lat, farmer_lon, b["latitude"], b["longitude"])
        breakdown = calculate_net_realization(
            offered_price=b["offered_price_per_quintal"],
            quantity_quintals=quantity,
            distance_km=dist,
            buyer_on_time_payment_pct=b["on_time_payment_pct"],
        )
        enriched.append({
            "name": b["name"],
            "buyer_type": b["buyer_type"],
            "offered_price": b["offered_price_per_quintal"],
            "distance_km": round(dist, 1),
            "on_time_pct": b["on_time_payment_pct"],
            "net_real_per_qtl": breakdown["net_realization_per_quintal"],
            "reliability_adj": breakdown["reliability_adjustment"],
            "reliability_discount_pct": breakdown["reliability_discount_pct"],
            "transport_cost": breakdown["transport_cost"],
        })

    by_price = sorted(enriched, key=lambda x: x["offered_price"], reverse=True)
    by_net = sorted(enriched, key=lambda x: x["net_real_per_qtl"], reverse=True)

    print(f"Commodity: {commodity} | Farmer: Aralamoodu, Kerala | Qty: {quantity} qtl")
    print("=" * 110)

    print("\n(A) Ranked by RAW OFFERED PRICE (descending)")
    print(f"{'Rank':<5} {'Buyer':<35} {'Type':<18} {'Price/Qtl':>10} {'Dist km':>8} {'Rel%':>5}")
    print("-" * 85)
    for i, r in enumerate(by_price, 1):
        print(f"{i:<5} {r['name']:<35} {r['buyer_type']:<18} Rs.{r['offered_price']:>6} {r['distance_km']:>7.1f} {r['on_time_pct']:>4}%")

    print(f"\n(B) Ranked by NET REALIZATION per quintal (descending)")
    print(f"{'Rank':<5} {'Buyer':<35} {'Type':<18} {'Net/Qtl':>10} {'Price/Qtl':>10} {'Dist km':>8} {'Rel%':>5}")
    print("-" * 95)
    for i, r in enumerate(by_net, 1):
        print(f"{i:<5} {r['name']:<35} {r['buyer_type']:<18} Rs.{r['net_real_per_qtl']:>7.2f} Rs.{r['offered_price']:>6} {r['distance_km']:>7.1f} {r['on_time_pct']:>4}%")

    # Check for distance-driven flip
    print("\n" + "=" * 110)
    naive_best = by_price[0]
    net_best = by_net[0]

    if naive_best["name"] != net_best["name"]:
        print("DISTANCE-DRIVEN RANKING FLIP DETECTED!")
        print(f"  Naive #1 (highest price) : {naive_best['name']} @ Rs.{naive_best['offered_price']}/qtl (dist: {naive_best['distance_km']}km)")
        print(f"  Net-Real #1 (best value) : {net_best['name']} @ Rs.{net_best['offered_price']}/qtl (dist: {net_best['distance_km']}km)")
        print(f"  Price difference         : Rs.{naive_best['offered_price'] - net_best['offered_price']}/qtl")
        print(f"  Net realization gap      : Rs.{net_best['net_real_per_qtl'] - naive_best['net_real_per_qtl']:.2f}/qtl in favour of {net_best['name']}")
    else:
        print("NO distance-driven ranking flip.")

    # Check for reliability-driven flip (buyers within 10km of each other)
    print("\n" + "=" * 110)
    print("RELIABILITY-DRIVEN FLIP CHECK (buyers within 10km of each other)")
    print("=" * 110)

    reliability_flip_found = False
    for i, a in enumerate(enriched):
        for j, b in enumerate(enriched):
            if i >= j:
                continue
            dist_diff = abs(a["distance_km"] - b["distance_km"])
            if dist_diff > 10:
                continue

            # Determine which has higher price and which has higher net
            if a["offered_price"] > b["offered_price"]:
                higher_price, lower_price = a, b
            elif b["offered_price"] > a["offered_price"]:
                higher_price, lower_price = b, a
            else:
                continue  # Same price, no flip possible

            # Flip = higher-priced buyer has LOWER net realization
            if higher_price["net_real_per_qtl"] < lower_price["net_real_per_qtl"]:
                reliability_flip_found = True
                print(f"\nRELIABILITY-DRIVEN FLIP FOUND!")
                print(f"  Distance band: {min(higher_price['distance_km'], lower_price['distance_km']):.1f} - {max(higher_price['distance_km'], lower_price['distance_km']):.1f} km (diff: {dist_diff:.1f} km)")
                print(f"")
                print(f"  {'':30} {'HIGHER-PRICE BUYER':>22}    {'LOWER-PRICE BUYER':>22}")
                print(f"  {'Name':<30} {higher_price['name']:>22}    {lower_price['name']:>22}")
                print(f"  {'Offered Price/Qtl':<30} Rs.{higher_price['offered_price']:>18}    Rs.{lower_price['offered_price']:>18}")
                print(f"  {'Distance (km)':<30} {higher_price['distance_km']:>21.1f}    {lower_price['distance_km']:>21.1f}")
                print(f"  {'On-time Payment %':<30} {higher_price['on_time_pct']:>20}%    {lower_price['on_time_pct']:>20}%")
                print(f"  {'Reliability Discount %':<30} {higher_price['reliability_discount_pct']:>20.2f}%    {lower_price['reliability_discount_pct']:>20.2f}%")
                print(f"  {'Reliability Adjustment (Rs.)':<30} Rs.{higher_price['reliability_adj']:>18.2f}    Rs.{lower_price['reliability_adj']:>18.2f}")
                print(f"  {'Transport Cost (Rs.)':<30} Rs.{higher_price['transport_cost']:>18.2f}    Rs.{lower_price['transport_cost']:>18.2f}")
                print(f"  {'NET REALIZATION/QTL':<30} Rs.{higher_price['net_real_per_qtl']:>18.2f}    Rs.{lower_price['net_real_per_qtl']:>18.2f}")
                print(f"")
                print(f"  --> {lower_price['name']} WINS by Rs.{lower_price['net_real_per_qtl'] - higher_price['net_real_per_qtl']:.2f}/qtl despite offering Rs.{higher_price['offered_price'] - lower_price['offered_price']}/qtl less,")
                print(f"      because {higher_price['name']}'s {higher_price['on_time_pct']}% payment reliability costs Rs.{higher_price['reliability_adj']:.2f} vs Rs.{lower_price['reliability_adj']:.2f}")

    if not reliability_flip_found:
        print("\nNO reliability-driven flip found among same-distance-band buyers.")
        print("Need to add a buyer to create this proof point.")


if __name__ == "__main__":
    check_ranking_flip()
