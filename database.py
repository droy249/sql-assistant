import sqlite3
from pathlib import Path

# Path to the SQLite database file
DB_PATH = Path("sales.db")

def get_connection():
    """Create and return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def init_database():
    """Create the sales table and seed it with sample data if empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create the sales table if it doesn't already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT NOT NULL,
            product_category TEXT NOT NULL,
            quarter TEXT NOT NULL,
            revenue REAL NOT NULL,
            units_sold INTEGER NOT NULL
        )
    """)

    # Only insert sample data if the table is empty
    cursor.execute("SELECT COUNT(*) FROM sales")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("North", "Electronics", "Q1 2025", 150000.00, 1200),
            ("North", "Electronics", "Q2 2025", 175000.00, 1400),
            ("North", "Clothing", "Q1 2025", 80000.00, 3200),
            ("North", "Clothing", "Q2 2025", 95000.00, 3800),
            ("South", "Electronics", "Q1 2025", 120000.00, 960),
            ("South", "Electronics", "Q2 2025", 140000.00, 1120),
            ("South", "Clothing", "Q1 2025", 65000.00, 2600),
            ("South", "Clothing", "Q2 2025", 72000.00, 2880),
            ("East", "Electronics", "Q1 2025", 200000.00, 1600),
            ("East", "Electronics", "Q2 2025", 220000.00, 1760),
            ("East", "Clothing", "Q1 2025", 110000.00, 4400),
            ("East", "Clothing", "Q2 2025", 125000.00, 5000),
            ("West", "Electronics", "Q1 2025", 180000.00, 1440),
            ("West", "Electronics", "Q2 2025", 195000.00, 1560),
            ("West", "Clothing", "Q1 2025", 90000.00, 3600),
            ("West", "Clothing", "Q2 2025", 105000.00, 4200),
        ]
        cursor.executemany(
            "INSERT INTO sales (region, product_category, quarter, revenue, units_sold) VALUES (?, ?, ?, ?, ?)",
            sample_data,
        )
        conn.commit()

    conn.close()

def query_database(sql: str) -> list[dict]:
    """Execute a SQL query and return results as a list of dictionaries."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results


if __name__ == "__main__":
    init_database()
    print("Database initialized with sample data.")