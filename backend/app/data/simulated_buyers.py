# SIMULATED DATA for hackathon demo 
# Structured to be realistic but not sourced from real buyers.

BUYERS = [
    # Kerala region (near Aralamoodu / Anchal) - focuses heavily on Cabbage, Carrot, Ginger, Banana
    {
        "buyer_id": "B001",
        "name": "Kerala Fresh Retailers",
        "buyer_type": "Retailer Chain",
        "commodities_bought": ["Cabbage", "Carrot", "Banana", "Brinjal"],
        "quality_grades_accepted": ["A", "B"],
        "min_lot_quantity_quintals": 5,
        "offered_price_per_quintal": 2200, # Near current cabbage price
        "latitude": 8.5241, # Trivandrum
        "longitude": 76.9366,
        "on_time_payment_pct": 92,
        "dispute_count_last_20_txns": 1,
        "fulfillment_rate_pct": 95
    },
    {
        "buyer_id": "B002",
        "name": "South India Processors Ltd",
        "buyer_type": "Processor",
        "commodities_bought": ["Cabbage", "Ginger(Green)"],
        "quality_grades_accepted": ["B", "C"], # Lower grade accepted
        "min_lot_quantity_quintals": 20,
        "offered_price_per_quintal": 1850,
        "latitude": 9.9312, # Kochi
        "longitude": 76.2673,
        "on_time_payment_pct": 98,
        "dispute_count_last_20_txns": 0,
        "fulfillment_rate_pct": 99
    },
    {
        "buyer_id": "B003",
        "name": "Aralamoodu Central Wholesale",
        "buyer_type": "Wholesaler",
        "commodities_bought": ["Cabbage", "Carrot", "Brinjal"],
        "quality_grades_accepted": ["A"],
        "min_lot_quantity_quintals": 10,
        "offered_price_per_quintal": 2300,
        "latitude": 8.3912, # Near Aralamoodu
        "longitude": 77.0620,
        "on_time_payment_pct": 75, # Less reliable
        "dispute_count_last_20_txns": 3,
        "fulfillment_rate_pct": 82
    },
    {
        "buyer_id": "B004",
        "name": "Trivandrum Institutional Suppliers",
        "buyer_type": "Institutional Buyer",
        "commodities_bought": ["Cabbage", "Banana", "Bhindi(Ladies Finger)"],
        "quality_grades_accepted": ["A", "B"],
        "min_lot_quantity_quintals": 15,
        "offered_price_per_quintal": 2150,
        "latitude": 8.5000, 
        "longitude": 76.9000,
        "on_time_payment_pct": 99,
        "dispute_count_last_20_txns": 0,
        "fulfillment_rate_pct": 98
    },
    {
        # This buyer offers more than Kerala Fresh Retailers (Rs.2250 vs Rs.2200)
        # but has a poor payment track record, creating a reliability-driven flip
        "buyer_id": "B014",
        "name": "Kattakada Vegmarket Traders",
        "buyer_type": "Wholesaler",
        "commodities_bought": ["Cabbage", "Brinjal", "Carrot"],
        "quality_grades_accepted": ["A", "B"],
        "min_lot_quantity_quintals": 8,
        "offered_price_per_quintal": 2250,
        "latitude": 8.4680, # Kattakada, ~25km from Aralamoodu (similar band to Kerala Fresh)
        "longitude": 76.9200,
        "on_time_payment_pct": 65, # Poor payment reliability
        "dispute_count_last_20_txns": 4,
        "fulfillment_rate_pct": 81
    },
    
    # Gujarat region (near Damnagar / Gondal) - focuses on Brinjal, Bhindi, Green Chilli, Cabbage
    {
        "buyer_id": "B005",
        "name": "Gondal Agro Wholesalers",
        "buyer_type": "Wholesaler",
        "commodities_bought": ["Brinjal", "Bhindi(Ladies Finger)", "Green Chilli"],
        "quality_grades_accepted": ["A", "B"],
        "min_lot_quantity_quintals": 8,
        "offered_price_per_quintal": 1200, 
        "latitude": 21.9619, # Gondal
        "longitude": 70.7923,
        "on_time_payment_pct": 85,
        "dispute_count_last_20_txns": 2,
        "fulfillment_rate_pct": 90
    },
    {
        "buyer_id": "B006",
        "name": "Rajkot Supermarkets",
        "buyer_type": "Retailer Chain",
        "commodities_bought": ["Brinjal", "Cabbage", "Carrot"],
        "quality_grades_accepted": ["A"],
        "min_lot_quantity_quintals": 3,
        "offered_price_per_quintal": 1400, # Premium for grade A
        "latitude": 22.3039, # Rajkot
        "longitude": 70.8022,
        "on_time_payment_pct": 95,
        "dispute_count_last_20_txns": 1,
        "fulfillment_rate_pct": 96
    },
    {
        "buyer_id": "B007",
        "name": "Surat Spices & Veg Processors",
        "buyer_type": "Processor",
        "commodities_bought": ["Green Chilli", "Ginger(Green)"],
        "quality_grades_accepted": ["A", "B", "C"],
        "min_lot_quantity_quintals": 25,
        "offered_price_per_quintal": 3500,
        "latitude": 21.1702, # Surat
        "longitude": 72.8311,
        "on_time_payment_pct": 97,
        "dispute_count_last_20_txns": 0,
        "fulfillment_rate_pct": 99
    },
    {
        "buyer_id": "B008",
        "name": "Damnagar Local Mandi Traders",
        "buyer_type": "Wholesaler",
        "commodities_bought": ["Bhindi(Ladies Finger)", "Brinjal", "Cauliflower"],
        "quality_grades_accepted": ["B", "C"],
        "min_lot_quantity_quintals": 5,
        "offered_price_per_quintal": 950,
        "latitude": 21.7200, # Damnagar
        "longitude": 71.5000,
        "on_time_payment_pct": 72,
        "dispute_count_last_20_txns": 4,
        "fulfillment_rate_pct": 80
    },
    
    # Uttar Pradesh region (near Raibareilly / Hasanpur) - focuses on Wheat, Maize, Mustard, Apple
    {
        "buyer_id": "B009",
        "name": "Lucknow Mills & Bakers",
        "buyer_type": "Processor",
        "commodities_bought": ["Wheat", "Maize"],
        "quality_grades_accepted": ["A", "B"],
        "min_lot_quantity_quintals": 50,
        "offered_price_per_quintal": 2500, 
        "latitude": 26.8467, # Lucknow
        "longitude": 80.9462,
        "on_time_payment_pct": 94,
        "dispute_count_last_20_txns": 1,
        "fulfillment_rate_pct": 97
    },
    {
        "buyer_id": "B010",
        "name": "Raibareilly Grain Traders",
        "buyer_type": "Wholesaler",
        "commodities_bought": ["Wheat", "Mustard", "Soyabean"],
        "quality_grades_accepted": ["A", "B", "C"],
        "min_lot_quantity_quintals": 30,
        "offered_price_per_quintal": 2450,
        "latitude": 26.2306, # Raibareilly
        "longitude": 81.2404,
        "on_time_payment_pct": 88,
        "dispute_count_last_20_txns": 2,
        "fulfillment_rate_pct": 92
    },
    {
        "buyer_id": "B011",
        "name": "UP Govt Food Corporation",
        "buyer_type": "Institutional Buyer",
        "commodities_bought": ["Wheat", "Lentil (Masur)(Whole)", "Arhar (Tur/Red Gram)(Whole)"],
        "quality_grades_accepted": ["A"],
        "min_lot_quantity_quintals": 100,
        "offered_price_per_quintal": 2400, # Usually fixed MSP, reliable payment but strict grading
        "latitude": 26.8500, 
        "longitude": 80.9500,
        "on_time_payment_pct": 99,
        "dispute_count_last_20_txns": 0,
        "fulfillment_rate_pct": 99
    },
    {
        "buyer_id": "B012",
        "name": "Kanpur Agri Exports",
        "buyer_type": "Processor",
        "commodities_bought": ["Mustard", "Soyabean", "Maize"],
        "quality_grades_accepted": ["A"],
        "min_lot_quantity_quintals": 40,
        "offered_price_per_quintal": 4200,
        "latitude": 26.4499, # Kanpur
        "longitude": 80.3319,
        "on_time_payment_pct": 96,
        "dispute_count_last_20_txns": 1,
        "fulfillment_rate_pct": 95
    },
    
    # Few cross-regional / national buyers
    {
        "buyer_id": "B013",
        "name": "National Supermarts",
        "buyer_type": "Retailer Chain",
        "commodities_bought": ["Apple", "Cabbage", "Carrot", "Onion"],
        "quality_grades_accepted": ["A"],
        "min_lot_quantity_quintals": 10,
        "offered_price_per_quintal": 2500,
        "latitude": 28.7041, # Delhi HQ, but buys nationally (assume distance is to local hub, using Delhi for now)
        "longitude": 77.1025,
        "on_time_payment_pct": 98,
        "dispute_count_last_20_txns": 0,
        "fulfillment_rate_pct": 98
    }
]
