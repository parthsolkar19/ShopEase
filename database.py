import sqlite3
from datetime import datetime

DB_NAME = "shop.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Bills table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            subtotal REAL NOT NULL,
            gst REAL NOT NULL,
            discount REAL NOT NULL,
            total REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Bill items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (bill_id) REFERENCES bills(id)
        )
    """)

    conn.commit()
    conn.close()


def add_product(name, category, price, stock):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, category, price, stock)
        VALUES (?, ?, ?, ?)
    """, (name, category, price, stock))

    conn.commit()
    conn.close()


def get_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, category, price, stock
        FROM products
        ORDER BY id DESC
    """)

    products = cursor.fetchall()
    conn.close()

    return products


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    conn.commit()
    conn.close()

def update_product(product_id, name, category, price, stock):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET name = ?, category = ?, price = ?, stock = ?
        WHERE id = ?
    """, (
        name,
        category,
        price,
        stock,
        product_id
    ))

    conn.commit()
    conn.close()

def update_stock(product_id, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET stock = stock - ?
        WHERE id = ?
    """, (quantity, product_id))

    conn.commit()
    conn.close()


def save_bill(customer_name, subtotal, gst, discount, total, cart):
    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save bill
    cursor.execute("""
        INSERT INTO bills
        (customer_name, subtotal, gst, discount, total, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        customer_name,
        subtotal,
        gst,
        discount,
        total,
        created_at
    ))

    bill_id = cursor.lastrowid

    # Save individual bill items
    for item in cart:
        cursor.execute("""
            INSERT INTO bill_items
            (bill_id, product_name, quantity, price, total)
            VALUES (?, ?, ?, ?, ?)
        """, (
            bill_id,
            item["name"],
            item["quantity"],
            item["price"],
            item["total"]
        ))

    # Reduce product stock
    for item in cart:
        cursor.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE id = ?
        """, (
            item["quantity"],
            item["id"]
        ))

    # Save everything
    conn.commit()
    conn.close()

    return bill_id


def get_bills():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, customer_name, subtotal, gst,
               discount, total, created_at
        FROM bills
        ORDER BY id DESC
    """)

    bills = cursor.fetchall()
    conn.close()

    return bills


def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()

    # Total products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Total stock
    cursor.execute(
        "SELECT COALESCE(SUM(stock), 0) FROM products"
    )
    total_stock = cursor.fetchone()[0]

    # Total bills
    cursor.execute("SELECT COUNT(*) FROM bills")
    total_bills = cursor.fetchone()[0]

    # Total sales
    cursor.execute(
        "SELECT COALESCE(SUM(total), 0) FROM bills"
    )
    total_sales = cursor.fetchone()[0]

    conn.close()

    return {
        "products": total_products,
        "stock": total_stock,
        "bills": total_bills,
        "sales": total_sales
    }


# Create database automatically
initialize_database()