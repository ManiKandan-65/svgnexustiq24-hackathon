import os
import csv
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
STORES_FILE = os.path.join(DATA_DIR, "stores.csv")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")


def generate_synthetic_data(force=False):
    """Generates realistic 90-day retail dataset using standard library csv module."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not force and (
        os.path.exists(STORES_FILE)
        and os.path.exists(PRODUCTS_FILE)
        and os.path.exists(INVENTORY_FILE)
        and os.path.exists(SALES_FILE)
    ):
        return

    print("[DataLoader] Generating realistic 90-day synthetic retail dataset (standard library only)...")
    random.seed(42)

    # 1. STORES
    stores = [
        {"store_id": "ST01", "store_name": "Chennai Central", "city": "Chennai", "region": "North Tamil Nadu"},
        {"store_id": "ST02", "store_name": "Coimbatore Main", "city": "Coimbatore", "region": "West Tamil Nadu"},
        {"store_id": "ST03", "store_name": "Madurai Plaza", "city": "Madurai", "region": "South Tamil Nadu"},
    ]
    with open(STORES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["store_id", "store_name", "city", "region"])
        writer.writeheader()
        writer.writerows(stores)

    # 2. PRODUCTS (40 products, 8 categories)
    raw_products = [
        # Electronics (01-05)
        ("PRD001", "Wireless Mouse", "Electronics", 450.0, 899.0),
        ("PRD002", "Mechanical Keyboard", "Electronics", 1800.0, 3499.0),
        ("PRD003", "USB-C Fast Charger", "Electronics", 350.0, 799.0),
        ("PRD004", "Power Bank 20000mAh", "Electronics", 900.0, 1999.0),
        ("PRD005", "Noise-Canceling Earbuds", "Electronics", 2200.0, 4999.0),

        # Accessories (06-10)
        ("PRD006", "Laptop Sleeve 15-inch", "Accessories", 400.0, 999.0),
        ("PRD007", "Adjustable Phone Stand", "Accessories", 150.0, 399.0),
        ("PRD008", "Smart Fitness Watch", "Accessories", 1500.0, 3299.0),
        ("PRD009", "Anti-Theft Backpack", "Accessories", 800.0, 1899.0),
        ("PRD010", "Leather Slim Wallet", "Accessories", 300.0, 749.0),

        # Home (11-15)
        ("PRD011", "LED Desk Lamp", "Home", 500.0, 1299.0),
        ("PRD012", "Bluetooth Speaker", "Electronics", 1100.0, 2499.0),
        ("PRD013", "Digital Wall Clock", "Home", 350.0, 849.0),
        ("PRD014", "Memory Foam Pillow", "Home", 700.0, 1599.0),
        ("PRD015", "Ergonomic Desk Chair", "Home", 4500.0, 9999.0),

        # Kitchen (16-20)
        ("PRD016", "Stainless Steel Water Bottle", "Kitchen", 250.0, 599.0),
        ("PRD017", "Digital Air Fryer", "Kitchen", 3200.0, 6999.0),
        ("PRD018", "Chef Knife Set 5-Piece", "Kitchen", 1200.0, 2799.0),
        ("PRD019", "Non-Stick Frying Pan", "Kitchen", 600.0, 1399.0),
        ("PRD020", "Glass Meal Containers 4-Pack", "Kitchen", 400.0, 999.0),

        # Personal Care (21-25)
        ("PRD021", "Electric Toothbrush", "Personal Care", 750.0, 1699.0),
        ("PRD022", "Ionic Hair Dryer", "Personal Care", 1100.0, 2499.0),
        ("PRD023", "Organic Shampoo 500ml", "Personal Care", 200.0, 499.0),
        ("PRD024", "Hydrating Skincare Serum", "Personal Care", 350.0, 899.0),
        ("PRD025", "Beard Trimmer Kit", "Personal Care", 650.0, 1499.0),

        # Stationery (26-30)
        ("PRD026", "Executive Hardbound Journal", "Stationery", 150.0, 399.0),
        ("PRD027", "Fine Gel Pen Set 10-Pack", "Stationery", 80.0, 249.0),
        ("PRD028", "Mesh Desk Organizer", "Stationery", 200.0, 499.0),
        ("PRD029", "Pastel Highlighter Pack", "Stationery", 90.0, 229.0),
        ("PRD030", "Sticky Notes Value Box", "Stationery", 70.0, 179.0),

        # Grocery (31-35)
        ("PRD031", "Arabica Coffee Beans 500g", "Grocery", 300.0, 699.0),
        ("PRD032", "Organic Green Tea 100 Bags", "Grocery", 180.0, 449.0),
        ("PRD033", "Artisanal Dark Chocolate 3-Pack", "Grocery", 220.0, 549.0),
        ("PRD034", "Raw California Almonds 500g", "Grocery", 320.0, 649.0),
        ("PRD035", "Extra Virgin Olive Oil 1L", "Grocery", 500.0, 1099.0),

        # Lifestyle (36-40)
        ("PRD036", "Eco Yoga Mat 6mm", "Lifestyle", 450.0, 1099.0),
        ("PRD037", "Insulated Travel Tumbler", "Lifestyle", 350.0, 799.0),
        ("PRD038", "Waterproof Travel Duffel", "Lifestyle", 900.0, 2199.0),
        ("PRD039", "UV Protection Sunglasses", "Lifestyle", 400.0, 999.0),
        ("PRD040", "Cotton Canvas Tote Bag", "Lifestyle", 120.0, 299.0)
    ]

    products = []
    for pid, pname, cat, ucost, sprice in raw_products:
        products.append({"product_id": pid, "product_name": pname, "category": cat})

    with open(PRODUCTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["product_id", "product_name", "category"])
        writer.writeheader()
        writer.writerows(products)

    # 3. INVENTORY SETUP WITH DEMO SCENARIOS
    inventory = []
    for store in stores:
        sid = store["store_id"]
        for pid, pname, cat, ucost, sprice in raw_products:
            reorder_level = 30
            stock = random.randint(40, 100)

            # DEMO SCENARIOS:
            if sid == "ST01" and pid == "PRD001":  # High stock-out risk (Wireless Mouse @ ST01)
                stock = 12
                reorder_level = 35
            elif sid == "ST02" and pid == "PRD015":  # Overstock (Ergonomic Chair @ ST02)
                stock = 250
                reorder_level = 20
            elif sid == "ST02" and pid == "PRD021":  # Medium stock-out risk (Electric Toothbrush @ ST02)
                stock = 42
                reorder_level = 40
            elif sid == "ST03" and pid == "PRD008":  # Sales spike (Smart Fitness Watch @ ST03)
                stock = 18
                reorder_level = 50

            inventory.append({
                "store_id": sid,
                "product_id": pid,
                "current_stock": stock,
                "reorder_level": reorder_level,
                "unit_cost": ucost,
                "selling_price": sprice
            })

    with open(INVENTORY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["store_id", "product_id", "current_stock", "reorder_level", "unit_cost", "selling_price"]
        )
        writer.writeheader()
        writer.writerows(inventory)

    # 4. SALES HISTORY (90 Days)
    end_date = datetime(2026, 9, 4)
    start_date = end_date - timedelta(days=89)

    sales_records = []
    for day_offset in range(90):
        current_day = start_date + timedelta(days=day_offset)
        date_str = current_day.strftime("%Y-%m-%d")

        for store in stores:
            sid = store["store_id"]
            for pid, pname, cat, ucost, sprice in raw_products:
                base_qty = 2
                if cat in ["Electronics", "Personal Care"]:
                    base_qty = 4
                elif cat in ["Grocery", "Stationery"]:
                    base_qty = 6

                # Demo Scenarios
                if sid == "ST01" and pid == "PRD001":  # Wireless Mouse high steady sales
                    qty = random.choice([4, 5, 5, 6, 6, 7])
                elif sid == "ST01" and pid == "PRD012":  # Bluetooth Speaker Sales Drop!
                    qty = random.randint(16, 24) if day_offset < 60 else random.randint(1, 3)
                elif sid == "ST03" and pid == "PRD008":  # Smart Watch Sales Spike!
                    qty = random.randint(0, 2) if day_offset < 75 else random.randint(12, 16)
                elif sid == "ST02" and pid == "PRD015":  # Overstock chair slow movement
                    qty = 1 if random.random() < 0.2 else 0
                else:
                    qty = max(0, base_qty + random.choice([-1, 0, 1, 2]))

                revenue = round(qty * sprice, 2)
                sales_records.append({
                    "date": date_str,
                    "store_id": sid,
                    "product_id": pid,
                    "quantity_sold": qty,
                    "revenue": revenue
                })

    with open(SALES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["date", "store_id", "product_id", "quantity_sold", "revenue"]
        )
        writer.writeheader()
        writer.writerows(sales_records)

    print(f"[DataLoader] Generated {len(sales_records)} sales rows across 90 days.")


_DATASET_CACHE = None

def load_dataset():
    """Loads CSV files into in-memory list-of-dicts with proper type casting."""
    global _DATASET_CACHE
    if _DATASET_CACHE is not None:
        return _DATASET_CACHE

    generate_synthetic_data()

    stores = []
    with open(STORES_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stores.append(row)

    products = []
    with open(PRODUCTS_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)

    inventory = []
    with open(INVENTORY_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            inventory.append({
                "store_id": row["store_id"],
                "product_id": row["product_id"],
                "current_stock": int(row["current_stock"]),
                "reorder_level": int(row["reorder_level"]),
                "unit_cost": float(row["unit_cost"]),
                "selling_price": float(row["selling_price"])
            })

    sales = []
    with open(SALES_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sales.append({
                "date": row["date"],
                "store_id": row["store_id"],
                "product_id": row["product_id"],
                "quantity_sold": int(row["quantity_sold"]),
                "revenue": float(row["revenue"])
            })

    _DATASET_CACHE = {
        "stores": stores,
        "products": products,
        "inventory": inventory,
        "sales": sales
    }
    return _DATASET_CACHE


def validate_data_quality(dataset):
    """Detects invalid records (negative stock, negative sales, unknown IDs)."""
    warnings = []
    valid_pids = {p["product_id"] for p in dataset["products"]}
    valid_sids = {s["store_id"] for s in dataset["stores"]}

    neg_stock = [inv for inv in dataset["inventory"] if inv["current_stock"] < 0]
    if neg_stock:
        warnings.append(f"DATA QUALITY WARNING: {len(neg_stock)} inventory records have negative stock.")

    neg_sales = [s for s in dataset["sales"] if s["quantity_sold"] < 0 or s["revenue"] < 0]
    if neg_sales:
        warnings.append(f"DATA QUALITY WARNING: {len(neg_sales)} sales records have negative values.")

    bad_pids = [inv for inv in dataset["inventory"] if inv["product_id"] not in valid_pids]
    if bad_pids:
        warnings.append(f"DATA QUALITY WARNING: {len(bad_pids)} inventory records have invalid product IDs.")

    return warnings


if __name__ == "__main__":
    generate_synthetic_data(force=True)
    ds = load_dataset()
    print("Stores:", len(ds["stores"]))
    print("Products:", len(ds["products"]))
    print("Inventory records:", len(ds["inventory"]))
    print("Sales records:", len(ds["sales"]))
