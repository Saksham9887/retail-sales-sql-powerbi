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
n_stores = 20
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
n_customers = 500
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

n_transactions = 15000
sales_rows = []
sid = 1
for _ in range(n_transactions):
    d = start_date + timedelta(days=random.randint(0, n_days))
    # seasonal boost: Nov/Dec higher volume
    if d.month in (11, 12) and random.random() < 0.4:
        d = d.replace(day=random.randint(1, 28))
    store = random.choice(stores["store_id"])
    product = products.sample(1).iloc[0]
    customer = random.choice(customers["customer_id"])
    qty = np.random.choice([1, 1, 1, 2, 2, 3, 4], p=[0.35,0.2,0.15,0.15,0.08,0.05,0.02])
    discount_pct = np.random.choice([0, 0, 0, 0.1, 0.15, 0.2], p=[0.55,0.15,0.1,0.1,0.06,0.04])
    unit_price = product["unit_price"]
    revenue = round(qty * unit_price * (1 - discount_pct), 2)
    sales_rows.append([sid, d.isoformat(), store, product["product_id"], customer, qty, discount_pct, revenue])
    sid += 1

sales = pd.DataFrame(sales_rows, columns=[
    "sale_id", "sale_date", "store_id", "product_id", "customer_id", "quantity", "discount_pct", "revenue"
])

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
