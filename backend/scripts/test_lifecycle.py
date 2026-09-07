import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def print_step(title, method, url, request_data=None, response=None):
    print(f"\n{'='*50}")
    print(f"STEP: {title}")
    print(f"{method} {url}")
    if request_data:
        print(f"REQUEST BODY:\n{json.dumps(request_data, indent=2)}")
    if response:
        print(f"RESPONSE [{response.status_code}]:\n{json.dumps(response.json(), indent=2)}")

def main():
    # Wait a bit for the server to be fully ready
    time.sleep(2)
    
    # 1. Create a Lot
    print("\n--- TESTING TRANSACTION LIFECYCLE ---")
    lot_data = {
        "commodity": "Cabbage",
        "quantity_quintals": 10.0,
        "quality_grade": "A",
        "state": "Kerala",
        "market": "Aralamoodu",
        "farmer_lat": 8.3912,
        "farmer_lon": 77.0620
    }
    r = requests.post(f"{BASE_URL}/lots", json=lot_data)
    print_step("Create Lot", "POST", f"{BASE_URL}/lots", lot_data, r)
    lot_id = r.json()["id"]

    # 2. Create an Offer
    offer_data = {
        "buyer_id": "buyer-123",
        "buyer_name": "Aralamoodu Central Wholesale",
        "offered_price_per_quintal": 2200.0,
        "net_realization_per_quintal": 1950.0
    }
    r = requests.post(f"{BASE_URL}/lots/{lot_id}/offers", json=offer_data)
    print_step("Create Offer", "POST", f"{BASE_URL}/lots/{lot_id}/offers", offer_data, r)
    offer_id = r.json()["id"]

    # 3. Accept the Offer
    accept_data = {"status": "ACCEPTED"}
    r = requests.patch(f"{BASE_URL}/offers/{offer_id}", json=accept_data)
    print_step("Accept Offer", "PATCH", f"{BASE_URL}/offers/{offer_id}", accept_data, r)

    # 4. Confirm Lot becomes SOLD and check Logistics auto-creation
    r = requests.get(f"{BASE_URL}/lots/{lot_id}")
    print_step("Verify Lot Status", "GET", f"{BASE_URL}/lots/{lot_id}", response=r)

    r = requests.get(f"{BASE_URL}/offers/{offer_id}")
    print_step("Verify Logistics Auto-created", "GET", f"{BASE_URL}/offers/{offer_id}", response=r)
    logistics_id = r.json()["logistics"]["id"]

    # 5. Update Logistics Status
    logistics_data = {"status": "SCHEDULED", "notes": "Truck assigned"}
    r = requests.patch(f"{BASE_URL}/logistics/{logistics_id}", json=logistics_data)
    print_step("Update Logistics (SCHEDULED)", "PATCH", f"{BASE_URL}/logistics/{logistics_id}", logistics_data, r)

    logistics_data = {"status": "IN_TRANSIT", "pickup_date": "2026-09-10"}
    r = requests.patch(f"{BASE_URL}/logistics/{logistics_id}", json=logistics_data)
    print_step("Update Logistics (IN_TRANSIT)", "PATCH", f"{BASE_URL}/logistics/{logistics_id}", logistics_data, r)

    # 6. Create Dispute
    dispute_data = {"reason": "Quality issue reported on delivery"}
    r = requests.post(f"{BASE_URL}/offers/{offer_id}/disputes", json=dispute_data)
    print_step("Create Dispute", "POST", f"{BASE_URL}/offers/{offer_id}/disputes", dispute_data, r)
    dispute_id = r.json()["id"]

    # 7. Resolve Dispute
    resolve_data = {"status": "RESOLVED", "resolution_notes": "Partial refund agreed"}
    r = requests.patch(f"{BASE_URL}/disputes/{dispute_id}", json=resolve_data)
    print_step("Resolve Dispute", "PATCH", f"{BASE_URL}/disputes/{dispute_id}", resolve_data, r)

if __name__ == "__main__":
    main()
