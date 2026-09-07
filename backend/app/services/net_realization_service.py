def transport_cost_per_trip(distance_km):
    """
    ASSUMPTION - illustrative logistics cost model for demo.
    Base loading/unloading cost + rate per km.
    Returns the total flat cost for the trip.
    """
    base_cost = 200 # Fixed loading/unloading
    rate_per_km = 2.5 # Cost per km
    return base_cost + (distance_km * rate_per_km)

def calculate_net_realization(offered_price, quantity_quintals, distance_km, mandi_commission_pct=6, reliability_discount_pct=None, buyer_on_time_payment_pct=None):
    """
    Calculates the net realization for a sale to a specific buyer.
    
    If reliability_discount_pct is not directly provided, it is calculated from 
    the buyer's on_time_payment_pct.
    """
    gross_revenue = offered_price * quantity_quintals
    
    # Flat trip cost (not per quintal) since one vehicle carries the whole lot
    transport_cost_total = transport_cost_per_trip(distance_km)
    
    commission_cost = gross_revenue * (mandi_commission_pct / 100)
    
    # Calculate reliability discount if not provided directly
    if reliability_discount_pct is None:
        if buyer_on_time_payment_pct is not None:
            # A damping factor, not a direct pass-through.
            reliability_discount_pct = (100 - buyer_on_time_payment_pct) * 0.1
        else:
            reliability_discount_pct = 0.0
            
    reliability_adjustment = gross_revenue * (reliability_discount_pct / 100)
    
    net_realization = gross_revenue - transport_cost_total - commission_cost - reliability_adjustment
    
    net_realization_per_quintal = net_realization / quantity_quintals if quantity_quintals > 0 else 0
    
    return {
        "gross_revenue": round(gross_revenue, 2),
        "transport_cost": round(transport_cost_total, 2),
        "commission_cost": round(commission_cost, 2),
        "reliability_adjustment": round(reliability_adjustment, 2),
        "net_realization": round(net_realization, 2),
        "net_realization_per_quintal": round(net_realization_per_quintal, 2),
        "reliability_discount_pct": round(reliability_discount_pct, 2)
    }
