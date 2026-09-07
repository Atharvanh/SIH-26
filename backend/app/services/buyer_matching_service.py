from app.data.simulated_buyers import BUYERS
from app.services.distance_service import estimate_road_distance_km
from app.services.net_realization_service import calculate_net_realization


def match_and_rank_buyers(commodity, quantity_quintals, quality_grade, farmer_lat, farmer_lon):
    """
    Filter eligible buyers, compute net realization for each, and return
    a list sorted by net_realization_per_quintal descending.
    """
    eligible = []
    for b in BUYERS:
        if commodity not in b["commodities_bought"]:
            continue
        if quality_grade not in b["quality_grades_accepted"]:
            continue
        if quantity_quintals < b["min_lot_quantity_quintals"]:
            continue
        eligible.append(b)

    if not eligible:
        return []

    # Compute distance and net realization for each eligible buyer
    results = []
    for b in eligible:
        distance_km = round(
            estimate_road_distance_km(farmer_lat, farmer_lon, b["latitude"], b["longitude"]),
            2,
        )
        reliability_discount_pct = (100 - b["on_time_payment_pct"]) * 0.1

        breakdown = calculate_net_realization(
            offered_price=b["offered_price_per_quintal"],
            quantity_quintals=quantity_quintals,
            distance_km=distance_km,
            buyer_on_time_payment_pct=b["on_time_payment_pct"],
        )

        results.append({
            "buyer_id": b["buyer_id"],
            "name": b["name"],
            "buyer_type": b["buyer_type"],
            "offered_price_per_quintal": b["offered_price_per_quintal"],
            "distance_km": distance_km,
            "on_time_payment_pct": b["on_time_payment_pct"],
            "dispute_count_last_20_txns": b["dispute_count_last_20_txns"],
            "fulfillment_rate_pct": b["fulfillment_rate_pct"],
            "breakdown": breakdown,
        })

    # Sort by raw offered price descending to assign naive_price_rank
    by_price = sorted(results, key=lambda x: x["offered_price_per_quintal"], reverse=True)
    naive_rank_map = {}
    for rank, entry in enumerate(by_price, 1):
        naive_rank_map[entry["buyer_id"]] = rank

    # Sort by net_realization_per_quintal descending (the real ranking)
    results.sort(key=lambda x: x["breakdown"]["net_realization_per_quintal"], reverse=True)

    for rank, entry in enumerate(results, 1):
        entry["net_realization_rank"] = rank
        entry["naive_price_rank"] = naive_rank_map[entry["buyer_id"]]

    return results
