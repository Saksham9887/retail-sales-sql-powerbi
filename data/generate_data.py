"""
Generates a synthetic but realistic multi-table retail sales dataset:
- regions.csv
- stores.csv
- products.csv
- customers.csv
- sales.csv (fact table)

Run: python generate_data.py
"""
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import date, timedelta

fake = Faker()
random.seed(42)
np.random.seed(42)

# ---------- Regions ----------
regions = pd.DataFrame({
    "region_id": range(1, 6),
    "region_name": ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
})

# ---------- Stores ----------
n_stores = 40
stores = pd.DataFrame({
    "store_id": range(1, n_stores + 1),
    "store_name": [f"Store #{i:03d}" for i in range(1, n_stores + 1)],
    "region_id": np.random.choice(regions["region_id"], n_stores),
    "city": [fake.city() for _ in range(n_stores)],
})

# ---------- Products ----------
categories = {
    "Electronics": ["Wireless Earbuds", "Bluetooth Speaker", "Laptop Stand", "USB-C Hub", "Smartwatch"],
    "Apparel": ["Cotton T-Shirt", "Denim Jeans", "Hoodie", "Running Shoes", "Winter Jacket"],
    "Home & Kitchen": ["Blender", "Air Fryer", "Cookware Set", "Coffee Maker", "Vacuum Cleaner"],
    "Beauty": ["Face Moisturizer", "Shampoo", "Perfume", "Lipstick Set", "Hair Dryer"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Water Bottle", "Bike Helmet", "Resistance Bands"],
}
rows = []
pid = 1
for cat, items in categories.items():
    for item in items:
        cost = round(np.random.uniform(5, 150), 2)
        price = round(cost * np.random.uniform(1.3, 2.2), 2)
        rows.append([pid, item, cat, cost, price])
        pid += 1
products = pd.DataFrame(rows, columns=["product_id", "product_name", "category", "unit_cost", "unit_price"])

# ---------- Customers ----------
n_customers = 8000
customers = pd.DataFrame({
    "customer_id": range(1, n_customers + 1),
    "customer_name": [fake.name() for _ in range(n_customers)],
    "email": [fake.email() for _ in range(n_customers)],
    "signup_date": [fake.date_between(start_date="-3y", end_date="-30d") for _ in range(n_customers)],
})

# ---------- Sales (fact table) ----------
start_date = date(2023, 1, 1)
end_date = date(2024, 12, 31)
n_days = (end_date - start_date).days

n_transactions = 520000

rand_days = np.random.randint(0, n_days + 1, n_transactions)
sale_dates = [start_date + timedelta(days=int(d)) for d in rand_days]
# seasonal boost: Nov/Dec higher volume (re-roll into Nov/Dec for ~40% chance if month already Nov/Dec)
seasonal_mask = np.array([d.month in (11, 12) for d in sale_dates]) & (np.random.random(n_transactions) < 0.4)
sale_dates = [
    d.replace(day=random.randint(1, 28)) if seasonal_mask[i] else d
    for i, d in enumerate(sale_dates)
]

store_ids = np.random.choice(stores["store_id"].values, n_transactions)
product_idx = np.random.randint(0, len(products), n_transactions)
customer_ids = np.random.choice(customers["customer_id"].values, n_transactions)
qty = np.random.choice([1, 1, 1, 2, 2, 3, 4], size=n_transactions, p=[0.35,0.2,0.15,0.15,0.08,0.05,0.02])
discount_pct = np.random.choice([0, 0, 0, 0.1, 0.15, 0.2], size=n_transactions, p=[0.55,0.15,0.1,0.1,0.06,0.04])

prod_ids = products["product_id"].values[product_idx]
unit_prices = products["unit_price"].values[product_idx]
revenue = np.round(qty * unit_prices * (1 - discount_pct), 2)

sales = pd.DataFrame({
    "sale_id": range(1, n_transactions + 1),
    "sale_date": [d.isoformat() for d in sale_dates],
    "store_id": store_ids,
    "product_id": prod_ids,
    "customer_id": customer_ids,
    "quantity": qty,
    "discount_pct": discount_pct,
    "revenue": revenue,
})

regions.to_csv("regions.csv", index=False)
stores.to_csv("stores.csv", index=False)
products.to_csv("products.csv", index=False)
customers.to_csv("customers.csv", index=False)
sales.to_csv("sales.csv", index=False)

print("Generated:")
print(f"  regions:   {len(regions)} rows")
print(f"  stores:    {len(stores)} rows")
print(f"  products:  {len(products)} rows")
print(f"  customers: {len(customers)} rows")
print(f"  sales:     {len(sales)} rows")
