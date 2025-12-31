import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ================== LOAD ENV ==================
load_dotenv()

DB_URL = os.getenv("POSTGRES_URL")

if not DB_URL:
    raise RuntimeError("POSTGRES_URL not found in .env")

# ================== CONNECT ==================
engine = create_engine(DB_URL)

# ================== SQL ==================
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    region TEXT NOT NULL,
    country TEXT NOT NULL,
    product TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    sale_date DATE NOT NULL
);
"""

INSERT_DATA_SQL = """
INSERT INTO sales (region, country, product, category, quantity, amount, sale_date)
VALUES
('Asia', 'India', 'Laptop', 'Electronics', 5, 400000, '2024-01-10'),
('Asia', 'India', 'Phone', 'Electronics', 10, 300000, '2024-01-15'),
('Asia', 'India', 'Headphones', 'Accessories', 20, 100000, '2024-02-05'),
('Asia', 'India', 'Tablet', 'Electronics', 4, 160000, '2024-03-01'),

('North America', 'USA', 'Laptop', 'Electronics', 6, 540000, '2024-01-12'),
('North America', 'USA', 'Phone', 'Electronics', 12, 480000, '2024-02-20'),
('North America', 'USA', 'Smartwatch', 'Accessories', 8, 160000, '2024-03-10'),

('Europe', 'Germany', 'Laptop', 'Electronics', 4, 360000, '2024-01-18'),
('Europe', 'Germany', 'Tablet', 'Electronics', 6, 240000, '2024-02-25'),
('Europe', 'France', 'Phone', 'Electronics', 9, 360000, '2024-03-15'),

('Middle East', 'UAE', 'Laptop', 'Electronics', 3, 270000, '2024-01-30'),
('Middle East', 'UAE', 'Phone', 'Electronics', 7, 280000, '2024-03-20');
"""

# ================== EXECUTE ==================
with engine.begin() as conn:
    conn.execute(text(CREATE_TABLE_SQL))
    conn.execute(text(INSERT_DATA_SQL))

print("✅ Sample data inserted successfully!")
