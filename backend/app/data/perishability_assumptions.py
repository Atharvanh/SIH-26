# ASSUMPTION - These values are NOT sourced from empirical data.
# They are rough estimates for DEMO PURPOSES ONLY in a hackathon context.
# In production, these should be replaced with actual post-harvest loss
# studies (e.g., ICAR/CIPHET data) and cold-chain availability factors.

PERISHABILITY = {
    # Highly perishable: rapid quality/weight loss, must sell within days
    # tier="high", daily_decay_pct=1.5%, max_safe_hold_days=4
    "Brinjal":                      {"tier": "high", "daily_decay_pct": 1.5, "max_safe_hold_days": 4},
    "Green Chilli":                 {"tier": "high", "daily_decay_pct": 1.5, "max_safe_hold_days": 4},
    "Bhindi(Ladies Finger)":        {"tier": "high", "daily_decay_pct": 1.5, "max_safe_hold_days": 4},
    "Banana":                       {"tier": "high", "daily_decay_pct": 1.5, "max_safe_hold_days": 4},
    "Mango":                        {"tier": "high", "daily_decay_pct": 1.5, "max_safe_hold_days": 4},
    "Apple":                        {"tier": "high", "daily_decay_pct": 1.0, "max_safe_hold_days": 7},

    # Semi-perishable: moderate shelf life with proper storage
    # tier="medium", daily_decay_pct=0.5%, max_safe_hold_days=10
    "Cabbage":                      {"tier": "medium", "daily_decay_pct": 0.5, "max_safe_hold_days": 10},
    "Cauliflower":                  {"tier": "medium", "daily_decay_pct": 0.5, "max_safe_hold_days": 10},
    "Carrot":                       {"tier": "medium", "daily_decay_pct": 0.5, "max_safe_hold_days": 10},
    "Onion":                        {"tier": "medium", "daily_decay_pct": 0.5, "max_safe_hold_days": 10},
    "Garlic":                       {"tier": "medium", "daily_decay_pct": 0.5, "max_safe_hold_days": 10},
    "Ginger(Green)":                {"tier": "medium", "daily_decay_pct": 0.5, "max_safe_hold_days": 10},

    # Storable: grains, pulses, oilseeds — can hold for months if dry
    # tier="low", daily_decay_pct=0.05%, max_safe_hold_days=90
    "Wheat":                        {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Maize":                        {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Soyabean":                     {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Mustard":                      {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Cotton":                       {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Lentil (Masur)(Whole)":        {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Green Gram (Moong)(Whole)":    {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Arhar (Tur/Red Gram)(Whole)":  {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Jowar(Sorghum)":               {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Bajra(Pearl Millet/Cumbu)":    {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Groundnut":                    {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
    "Gur(Jaggery)":                 {"tier": "low", "daily_decay_pct": 0.05, "max_safe_hold_days": 90},
}

# Default for any commodity not explicitly listed
DEFAULT_PERISHABILITY = {"tier": "medium", "daily_decay_pct": 0.5, "max_safe_hold_days": 10}


def get_perishability(commodity):
    """Return perishability info for a commodity, falling back to default."""
    return PERISHABILITY.get(commodity, DEFAULT_PERISHABILITY)
