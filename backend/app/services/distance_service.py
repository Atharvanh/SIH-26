import math

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees).
    """
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return c * r

def estimate_road_distance_km(lat1, lon1, lat2, lon2):
    """
    Estimates road distance by applying a standard approximation multiplier 
    (1.3) to the straight-line haversine distance.
    This accounts for roads not being perfectly straight.
    """
    straight_line_dist = haversine_distance_km(lat1, lon1, lat2, lon2)
    return straight_line_dist * 1.3
