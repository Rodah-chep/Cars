import requests
import json
import csv
import base64
from datetime import datetime, timedelta

BASE_URL = "https://cars360backend-prod.cars360.co.ke/api/cars/"
COUNT_URL = "https://cars360backend-prod.cars360.co.ke/api/cars/count/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

def generate_cursor(dt):
    ts = dt.strftime("%Y-%m-%d %H:%M:%S.%f") + "+00:00"
    ts = ts.replace(" ", "+").replace(":", "%3A")
    ts = ts[:ts.rfind("+")] + "%2B" + ts[ts.rfind("+")+1:]
    return base64.b64encode(f"p={ts}".encode()).decode()

def fetch(cursor=None):
    url = f"{BASE_URL}?cursor={cursor}" if cursor else BASE_URL
    try:
        return requests.get(url, headers=HEADERS, timeout=10).json()
    except:
        return []

# Get total count
try:
    total = requests.get(COUNT_URL, headers=HEADERS, timeout=10).json().get("count", 0)
    print(f"Total cars in database: {total:,}")
except:
    total = 0

# Collect all cars
all_cars = {}
now = datetime.now()

print(f"Scanning time slots...")

# Scan current day with finer granularity
for hour in range(24):
    for minute in range(0, 60, 10):  # Every 10 minutes
        cursor = generate_cursor(datetime(now.year, now.month, now.day, hour, minute, 0))
        for car in fetch(cursor):
            if car.get("id") and car["id"] not in all_cars:
                all_cars[car["id"]] = car

print(f"Found {len(all_cars)} unique cars")

# Save
if all_cars:
    records = []
    for c in all_cars.values():
        s = c.get("seller_info", {}) or {}
        records.append({
            "id": c.get("id"),
            "display_name": c.get("display_name"),
            "make_name": c.get("make_name"),
            "model_name": c.get("model_name"),
            "year": c.get("year"),
            "color": c.get("color"),
            "condition": c.get("condition"),
            "vehicle_type": c.get("vehicle_type"),
            "fuel_type": c.get("fuel_type"),
            "transmission": c.get("transmission"),
            "engine_size": c.get("engine_size"),
            "is_active": c.get("is_active"),
            "asking_price": c.get("asking_price"),
            "pricing_type": c.get("pricing_type"),
            "discount_price": c.get("discount_price"),
            "discount_percentage": c.get("discount_percentage"),
            "monthly_repayment": c.get("monthly_repayment"),
            "deposit_amount": c.get("deposit_amount"),
            "maximum_finance_amount": c.get("maximum_finance_amount"),
            "seats": c.get("seats"),
            "mileage": c.get("mileage"),
            "is_deal_of_week": c.get("is_deal_of_week"),
            "views_count": c.get("views_count"),
            "clicks_count": c.get("clicks_count"),
            "top_search": c.get("top_search"),
            "location_name": c.get("location_name"),
            "location_parent_name": c.get("location_parent_name_1"),
            "description": (c.get("description") or "")[:200],
            
            "seller_id": s.get("id"),
            "seller_user_id": s.get("user_id"),
            "seller_business_name": s.get("business_name"),
            "seller_phone": s.get("phone_number"),
            "seller_type_display": s.get("seller_type_display"),
            "created_at": c.get("created_at"),
        })
    
    with open("car_listings_2.csv", "w", newline="", encoding="utf-8") as f:
        fields = [k for k in records[0].keys() if k != 'created_at']
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(records)
    
    with open("car_listings.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(records)} records to CSV and JSON")
    
    # Summary
    makes = {}
    years = []
    prices = []
    for r in records:
        m = r.get("make_name") or "Unknown"
        makes[m] = makes.get(m, 0) + 1
        if r.get("year"):
            years.append(r["year"])
        if r.get("asking_price"):
            try:
                prices.append(float(r["asking_price"]))
            except:
                pass
    
    print(f"\n📊 Summary:")
    print(f"   Top makes: {sorted(makes.items(), key=lambda x: -x[1])[:5]}")
    if years:
        print(f"   Year range: {min(years)} - {max(years)}")
    if prices:
        print(f"   Price range: KES {min(prices):,.0f} - {max(prices):,.0f}")