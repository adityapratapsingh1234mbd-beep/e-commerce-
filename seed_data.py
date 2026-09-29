"""Generates realistic demo products, customers and ~1,300 historical transactions."""
import random
from contextlib import closing
from datetime import datetime, timedelta

import db

# (name, price in INR, discount %, base rating, short description)
PRODUCTS = {
    "Electronics": [
        ("boAt Rockerz 450 Bluetooth Headphones", 1499, 20, 4.2, "Wireless on-ear, 15h battery"),
        ("Redmi Note 13 Smartphone 128GB", 17999, 10, 4.3, "6.67 inch AMOLED, 108MP camera"),
        ("Realme Buds Air 5 Earbuds", 2999, 15, 4.1, "ANC earbuds with fast charging"),
        ("Mi Smart Band 8", 2499, 12, 4.2, "1.62 inch AMOLED fitness tracker"),
        ("Lenovo IdeaPad Slim 3 Laptop", 42990, 8, 4.4, "i5, 16GB RAM, 512GB SSD"),
        ("Samsung 25W Fast Charger", 1299, 25, 4.0, "USB-C super fast wall charger"),
        ("Portronics 20000mAh Power Bank", 1799, 30, 4.1, "Dual output, fast charging"),
        ("JBL Go 3 Bluetooth Speaker", 2999, 18, 4.5, "Portable waterproof speaker"),
        ("TP-Link AC1200 WiFi Router", 1599, 10, 4.0, "Dual band gigabit router"),
        ("Logitech M235 Wireless Mouse", 799, 5, 4.3, "Compact wireless optical mouse"),
    ],
    "Fashion": [
        ("Levi's Men's Slim Fit Jeans", 2199, 30, 4.2, "Stretch denim, mid rise"),
        ("Allen Solly Formal Shirt", 1499, 25, 4.0, "Regular fit cotton shirt"),
        ("Women's Cotton Straight Kurta", 999, 40, 4.1, "Printed everyday kurta"),
        ("Puma Men's Running Shoes", 3499, 35, 4.3, "Lightweight breathable trainers"),
        ("Fastrack Analog Watch", 1795, 15, 4.1, "Water resistant, leather strap"),
        ("Anarkali Party Wear Dress", 2299, 45, 4.0, "Festive georgette Anarkali"),
        ("Roadster Fleece Hoodie", 1199, 50, 4.2, "Warm unisex pullover hoodie"),
        ("Wildcraft 35L Backpack", 1399, 20, 4.4, "Laptop compartment, rain cover"),
        ("Aviator UV400 Sunglasses", 1999, 30, 4.0, "Polarised metal frame"),
        ("Peter England Slim Blazer", 3999, 40, 4.1, "Single breasted formal blazer"),
    ],
    "Home & Kitchen": [
        ("Prestige Induction Cooktop", 2499, 22, 4.2, "1900W with auto-cook menus"),
        ("Milton Steel Water Bottle 1L", 649, 10, 4.5, "Vacuum insulated, 24h cold"),
        ("Pigeon Non-Stick Cookware Set", 1899, 35, 4.1, "3-piece induction base set"),
        ("Philips Mixer Grinder 750W", 3299, 20, 4.4, "3 stainless steel jars"),
        ("Wakefit Memory Foam Pillow", 899, 25, 4.3, "Orthopedic contour pillow"),
        ("Bajaj Room Heater 2000W", 1999, 15, 4.0, "Fan heater with thermostat"),
        ("Cello Storage Container Set", 799, 30, 4.2, "Airtight 12-piece set"),
        ("Borosil Glass Dinner Set", 2599, 28, 4.3, "18-piece microwave safe set"),
        ("Havells Ceiling Fan 1200mm", 2899, 12, 4.2, "Energy saving 5-star fan"),
        ("Eureka Forbes Vacuum Cleaner", 4999, 32, 4.1, "1200W bagless vacuum"),
    ],
    "Beauty": [
        ("Lakme Absolute Matte Lipstick", 599, 20, 4.2, "Long lasting matte finish"),
        ("Nivea Nourishing Body Lotion", 349, 15, 4.4, "48h deep moisture, 400ml"),
        ("Himalaya Neem Face Wash", 199, 10, 4.3, "Purifying, for oily skin"),
        ("Maybelline Colossal Kajal", 249, 12, 4.4, "Smudge proof, 12h wear"),
        ("L'Oreal Total Repair Shampoo", 449, 18, 4.2, "For damaged hair, 650ml"),
        ("Mamaearth Vitamin C Serum", 599, 25, 4.1, "Brightening face serum"),
        ("Biotique SPF 50 Sunscreen", 379, 10, 4.0, "Broad spectrum, lightweight"),
        ("WOW Aloe Vera Gel", 299, 20, 4.3, "Multipurpose skin and hair gel"),
        ("Engage Perfume Spray", 299, 15, 4.0, "Long lasting fragrance for men"),
        ("Cetaphil Daily Moisturiser", 499, 8, 4.5, "Gentle for sensitive skin"),
    ],
    "Sports": [
        ("Yonex Astrox Badminton Racquet", 1299, 20, 4.3, "Graphite frame, with cover"),
        ("Nivia Storm Football Size 5", 599, 10, 4.2, "Machine stitched match ball"),
        ("SG Kashmir Willow Cricket Bat", 2499, 25, 4.1, "Full size, leather ball ready"),
        ("Cosco 6mm Yoga Mat", 699, 30, 4.3, "Anti-skid with carry strap"),
        ("Adjustable Dumbbell Set 20kg", 2199, 35, 4.2, "Home gym plates and rods"),
        ("Speed Skipping Rope", 249, 15, 4.0, "Adjustable ball bearing rope"),
        ("Boldfit Gym Gloves", 399, 40, 4.1, "Padded grip workout gloves"),
        ("Vector X Cycling Helmet", 1199, 22, 4.2, "Adjustable ventilated helmet"),
        ("Speedo Swimming Goggles", 599, 18, 4.3, "Anti-fog UV protection"),
        ("Protein Shaker Bottle 700ml", 299, 10, 4.4, "Leak proof with mixer ball"),
    ],
    "Books": [
        ("Atomic Habits - James Clear", 499, 30, 4.7, "Build good habits, break bad ones"),
        ("The Alchemist - Paulo Coelho", 299, 20, 4.6, "A fable about following dreams"),
        ("Rich Dad Poor Dad", 350, 25, 4.5, "Personal finance classic"),
        ("Wings of Fire - APJ Abdul Kalam", 250, 15, 4.7, "Autobiography of a missile man"),
        ("Python Crash Course", 899, 20, 4.6, "Hands-on programming introduction"),
        ("Think and Grow Rich", 199, 35, 4.4, "Classic on success mindset"),
        ("The Psychology of Money", 349, 28, 4.6, "Timeless lessons on wealth"),
        ("Ikigai", 299, 22, 4.3, "Japanese secret to a long life"),
        ("Deep Work - Cal Newport", 399, 25, 4.5, "Rules for focused success"),
        ("Data Science from Scratch", 799, 18, 4.4, "Core data science with Python"),
    ],
}

FIRST = ["Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Karan", "Rahul", "Siddharth", "Ishaan", "Kabir",
         "Ananya", "Diya", "Priya", "Neha", "Sneha", "Kavya", "Pooja", "Riya", "Meera", "Isha",
         "Amit", "Vikram", "Suresh", "Manoj", "Deepak", "Anjali", "Sunita", "Divya", "Nikhil", "Tanvi"]
LAST = ["Sharma", "Verma", "Patel", "Reddy", "Nair", "Iyer", "Gupta", "Singh", "Mehta", "Joshi",
        "Kulkarni", "Das", "Banerjee", "Chopra", "Kapoor", "Menon", "Rao", "Bhatt", "Malhotra", "Pillai"]


def _customers(rng):
    rows, used = [], set()
    while len(rows) < 100:
        name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
        if name in used:
            continue
        used.add(name)
        age = min(65, max(18, int(rng.gauss(32, 10))))
        cid = f"C{len(rows) + 1:03d}"
        email = name.lower().replace(" ", ".") + "@example.com"
        rows.append((cid, name, age, rng.choice(db.LOCATIONS), email))
    return rows


def _category_weights(age):
    if age < 26:
        return [3.0, 3.0, 1.0, 2.0, 2.5, 2.0]
    if age < 40:
        return [2.5, 2.0, 2.0, 2.0, 1.5, 2.0]
    return [1.5, 1.0, 3.5, 1.5, 1.0, 2.5]


def seed(n_orders=1300):
    rng = random.Random(42)
    products = []
    pid = 1
    for cat in db.CATEGORIES:
        for name, price, disc, rating, desc in PRODUCTS[cat]:
            products.append((f"P{pid:03d}", name, cat, float(price), float(disc), rating, desc))
            pid += 1
    by_cat = {c: [p for p in products if p[2] == c] for c in db.CATEGORIES}
    customers = _customers(rng)
    now = datetime.now()

    orders = []
    for _ in range(n_orders):
        cust = rng.choice(customers)
        when = now - timedelta(days=rng.randint(1, 365), hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
        method = rng.choices(db.PAYMENT_METHODS, [0.5, 0.3, 0.2])[0]
        n_items = rng.choices([1, 2, 3], [0.6, 0.3, 0.1])[0]
        chosen, lines = set(), []
        while len(lines) < n_items:
            cat = rng.choices(db.CATEGORIES, _category_weights(cust[2]))[0]
            p = rng.choice(by_cat[cat])
            if p[0] in chosen:
                continue
            chosen.add(p[0])
            qty = rng.choices([1, 2, 3, 4], [0.65, 0.22, 0.09, 0.04])[0]
            disc = p[4] if rng.random() < 0.7 else float(rng.choice([0, 5, 10, 15, 20]))
            rating = int(min(5, max(1, round(p[5] + rng.gauss(0, 0.8)))))
            total = round(p[3] * qty * (1 - disc / 100), 2)
            lines.append((p, qty, disc, rating, total))
        orders.append((when, cust, method, lines))
    orders.sort(key=lambda o: o[0])

    with closing(db.conn()) as c:
        c.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?)", products)
        c.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", customers)
        for i, (when, cust, method, lines) in enumerate(orders, start=1):
            oid = f"ORD{1000 + i}"
            address = f"{rng.randint(1, 250)}, {rng.choice(['MG Road', 'Park Street', 'Gandhi Nagar', 'Lake View', 'Civil Lines'])}, {cust[3]}"
            for p, qty, disc, rating, total in lines:
                c.execute(
                    "INSERT INTO transactions (order_id, customer_id, customer_name, age, location, product_id, "
                    "product_name, category, price, quantity, discount, rating, order_date, payment_method, "
                    "total_amount, delivery_address) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (oid, cust[0], cust[1], cust[2], cust[3], p[0], p[1], p[2], p[3], qty, disc, rating,
                     when.strftime("%Y-%m-%d %H:%M:%S"), method, total, address),
                )
        c.commit()
    db.export_csv()
