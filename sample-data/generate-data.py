# This script is to generate sample data for the ETL process
import os
import duckdb
from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta

# Initialize Faker and DB connection
fake = Faker()
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.makedirs(project_root, exist_ok=True)
db_path = os.path.join(project_root, "local_warehouse.duckdb")
con = duckdb.connect(db_path)

# Configuration
NUM_USERS = 500
NUM_PRODUCTS = 50
NUM_ORDERS = 1000
NUM_CLICKS = 5000

# 1. Generate Products Reference Table
products = []
categories = ['Electronics', 'Apparel', 'Home', 'Beauty', 'Sports']
for p_id in range(1, NUM_PRODUCTS + 1):
    products.append({
        "product_id": p_id,
        "product_name": fake.catch_phrase(),
        "category": random.choice(categories),
        "price": round(random.uniform(5.0, 500.0), 2)
    })
df_products = pd.DataFrame(products)

# 2. Generate Users
users = []
for u_id in range(1, NUM_USERS + 1):
    users.append({
        "user_id": u_id,
        "email": fake.email(),
        "signup_date": fake.date_between(start_date="-1y", end_date="today")
    })
df_users = pd.DataFrame(users)

# 3. Generate Orders & Order Items
orders = []
order_items = []
order_item_id = 1

for o_id in range(1, NUM_ORDERS + 1):
    user_id = random.randint(1, NUM_USERS)
    order_date = fake.date_time_between(start_date="-30d", end_date="now")
    orders.append({
        "order_id": o_id,
        "user_id": user_id,
        "order_timestamp": order_date,
        "status": random.choice(['completed', 'completed', 'completed', 'returned', 'cancelled'])
    })
    
    # 1 to 3 items per order
    for _ in range(random.randint(1, 3)):
        prod = random.choice(products)
        order_items.append({
            "order_item_id": order_item_id,
            "order_id": o_id,
            "product_id": prod["product_id"],
            "quantity": random.randint(1, 2),
            "item_price": prod["price"]
        })
        order_item_id += 1

df_orders = pd.DataFrame(orders)
df_order_items = pd.DataFrame(order_items)

# 4. Generate Clickstream Behavioral Logs
clicks = []
actions = ['view', 'view', 'add_to_cart', 'click']
for c_id in range(1, NUM_CLICKS + 1):
    clicks.append({
        "click_id": c_id,
        "user_id": random.randint(1, NUM_USERS),
        "product_id": random.randint(1, NUM_PRODUCTS),
        "action": random.choice(actions),
        "click_timestamp": fake.date_time_between(start_date="-30d", end_date="now")
    })
df_clicks = pd.DataFrame(clicks)

# Write DataFrames directly to DuckDB Raw Schema
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
con.execute("CREATE TABLE IF NOT EXISTS raw.products AS SELECT * FROM df_products")
con.execute("CREATE TABLE IF NOT EXISTS raw.users AS SELECT * FROM df_users")
con.execute("CREATE TABLE IF NOT EXISTS raw.orders AS SELECT * FROM df_orders")
con.execute("CREATE TABLE IF NOT EXISTS raw.order_items AS SELECT * FROM df_order_items")
con.execute("CREATE TABLE IF NOT EXISTS raw.clickstream AS SELECT * FROM df_clicks")

print(f"Data pipeline complete. Seeded data successfully into: {db_path}")
con.close()

