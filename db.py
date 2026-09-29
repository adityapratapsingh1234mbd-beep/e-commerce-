"""Database layer: SQLite storage + CSV export for the ONLINE E-COMMERCE project."""
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "ecommerce.db"
CSV_PATH = DATA_DIR / "transactions.csv"

CATEGORIES = ["Electronics", "Fashion", "Home & Kitchen", "Beauty", "Sports", "Books"]
LOCATIONS = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata",
             "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Kochi"]
PAYMENT_METHODS = ["UPI", "Card", "Cash on Delivery"]

SORTS = {
    "Featured": "product_id",
    "Price: Low to High": "price * (1 - discount / 100.0) ASC",
    "Price: High to Low": "price * (1 - discount / 100.0) DESC",
    "Rating: High to Low": "rating DESC",
    "Biggest Discount": "discount DESC",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id   TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    age           INTEGER,
    location      TEXT,
    email         TEXT
);
CREATE TABLE IF NOT EXISTS products (
    product_id   TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL,
    price        REAL NOT NULL,
    discount     REAL DEFAULT 0,
    rating       REAL,
    description  TEXT
);
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id         TEXT,
    customer_id      TEXT,
    customer_name    TEXT,
    age              INTEGER,
    location         TEXT,
    product_id       TEXT,
    product_name     TEXT,
    category         TEXT,
    price            REAL,
    quantity         INTEGER,
    discount         REAL,
    rating           REAL,
    order_date       TEXT,
    payment_method   TEXT,
    total_amount     REAL,
    delivery_address TEXT,
    delivery_lat    REAL,
    delivery_lng    REAL,
    order_status    TEXT DEFAULT 'Placed'
);
"""

TRANSACTION_COLUMNS = [
    "transaction_id", "order_id", "customer_id", "customer_name", "age", "location",
    "product_id", "product_name", "category", "price", "quantity", "discount",
    "rating", "order_date", "payment_method", "total_amount", "delivery_address",
    "delivery_lat", "delivery_lng", "order_status",
]


def conn():
    DATA_DIR.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def query(sql, params=()):
    with closing(conn()) as c:
        return pd.read_sql_query(sql, c, params=params)


def init_db():
    with closing(conn()) as c:
        c.executescript(SCHEMA)
        # Lightweight migrations keep an already-created demo database compatible.
        existing = {r[1] for r in c.execute("PRAGMA table_info(transactions)").fetchall()}
        for col, ddl in [("delivery_lat", "REAL"), ("delivery_lng", "REAL"), ("order_status", "TEXT DEFAULT 'Delivered'")]:
            if col not in existing:
                c.execute(f"ALTER TABLE transactions ADD COLUMN {col} {ddl}")
        n = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        c.commit()
    if n == 0:
        import seed_data
        seed_data.seed()
    export_csv()


def export_csv():
    df = query(f"SELECT {', '.join(TRANSACTION_COLUMNS)} FROM transactions ORDER BY transaction_id")
    df.to_csv(CSV_PATH, index=False)


# ---------- products ----------
def get_products(category="All", search="", sort="Featured"):
    sql, params = "SELECT * FROM products WHERE 1=1", []
    if category and category != "All":
        sql += " AND category = ?"
        params.append(category)
    if search and search.strip():
        sql += " AND (product_name LIKE ? OR description LIKE ? OR category LIKE ?)"
        like = f"%{search.strip()}%"
        params += [like, like, like]
    sql += f" ORDER BY {SORTS.get(sort, 'product_id')}"
    return query(sql, params)


def get_product(product_id):
    df = query("SELECT * FROM products WHERE product_id = ?", (product_id,))
    return None if df.empty else df.iloc[0].to_dict()


def get_product_reviews(product_id):
    df = query("SELECT AVG(rating) AS avg_rating, COUNT(rating) AS n FROM transactions "
               "WHERE product_id = ? AND rating IS NOT NULL", (product_id,))
    r = df.iloc[0]
    return (None if pd.isna(r["avg_rating"]) else float(r["avg_rating"])), int(r["n"])


# ---------- customers ----------
def get_customers():
    return query("SELECT * FROM customers ORDER BY customer_id")


def get_customer(customer_id):
    df = query("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    if df.empty:
        return None
    row = df.iloc[0].to_dict()
    row["age"] = int(row["age"])
    return row


def add_customer(name, age, location, email=""):
    with closing(conn()) as c:
        last = c.execute("SELECT MAX(CAST(SUBSTR(customer_id, 2) AS INTEGER)) FROM customers").fetchone()[0] or 0
        cid = f"C{last + 1:03d}"
        c.execute("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", (cid, name, int(age), location, email))
        c.commit()
    return cid


# ---------- orders ----------
def place_order(customer, items, method, address, latitude=None, longitude=None):
    """items = list of (product_dict, quantity). Returns the new order_id."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with closing(conn()) as c:
        last = c.execute("SELECT MAX(CAST(SUBSTR(order_id, 4) AS INTEGER)) FROM transactions").fetchone()[0] or 1000
        order_id = f"ORD{last + 1}"
        for p, qty in items:
            price, disc, qty = float(p["price"]), float(p["discount"]), int(qty)
            total = round(price * qty * (1 - disc / 100), 2)
            c.execute(
                "INSERT INTO transactions (order_id, customer_id, customer_name, age, location, product_id, "
                "product_name, category, price, quantity, discount, rating, order_date, payment_method, "
                "total_amount, delivery_address, delivery_lat, delivery_lng, order_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (order_id, customer["customer_id"], customer["customer_name"], int(customer["age"]),
                 customer["location"], p["product_id"], p["product_name"], p["category"], price, qty,
                 disc, None, now, method, total, address, latitude, longitude, "Placed"),
            )
        c.commit()
    export_csv()
    return order_id


def get_order(order_id, customer_id=None):
    sql = "SELECT * FROM transactions WHERE order_id = ?"
    params = [order_id]
    if customer_id:
        sql += " AND customer_id = ?"
        params.append(customer_id)
    return query(sql, params)


def get_orders(customer_id):
    return query("SELECT * FROM transactions WHERE customer_id = ? ORDER BY order_date DESC, transaction_id",
                 (customer_id,))


def update_rating(transaction_id, rating):
    with closing(conn()) as c:
        c.execute("UPDATE transactions SET rating = ? WHERE transaction_id = ?", (float(rating), int(transaction_id)))
        c.commit()
    export_csv()


def get_stats():
    r = query("SELECT (SELECT COUNT(*) FROM products) AS products, "
              "(SELECT COUNT(*) FROM customers) AS customers, "
              "(SELECT COUNT(DISTINCT order_id) FROM transactions) AS orders").iloc[0]
    return {k: int(r[k]) for k in ("products", "customers", "orders")}
