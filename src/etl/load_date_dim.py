import pandas as pd
import psycopg2
from configparser import ConfigParser

# Read config.ini
config = ConfigParser()
config.read('/Users/mac/Desktop/Projects/bank-health-kpi-dashboard/config.ini')

db_params = {
    "host": config.get("postgresql", "host"),
    "port": config.get("postgresql", "port"),
    "dbname": config.get("postgresql", "dbname"),
    "user": config.get("postgresql", "user"),
    "password": config.get("postgresql", "password")
}

# Generate date range (2000–2030)
date_range = pd.date_range(start="2000-01-01", end="2030-12-31", freq="D")

df = pd.DataFrame({
    "date": date_range,
})
df["date_id"] = df["date"].dt.strftime("%Y%m%d").astype(int)   # surrogate key
df["year"] = df["date"].dt.year
df["quarter"] = df["date"].dt.quarter
df["month"] = df["date"].dt.month
df["month_name"] = df["date"].dt.strftime("%B")
df["day"] = df["date"].dt.day
df["day_of_week"] = df["date"].dt.dayofweek + 1   # 1=Monday, 7=Sunday
df["weekday_name"] = df["date"].dt.strftime("%A")

# Connect to kpi_bank DB
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Create date_dim table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS date_dim (
    date_id INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20),
    day INT,
    day_of_week INT,
    weekday_name VARCHAR(20)
);
""")
conn.commit()

# Insert (UPSERT)
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO date_dim (date_id, full_date, year, quarter, month, month_name, day, day_of_week, weekday_name)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (date_id) DO NOTHING;
    """, (
        row["date_id"], row["date"], row["year"], row["quarter"], row["month"],
        row["month_name"], row["day"], row["day_of_week"], row["weekday_name"]
    ))

conn.commit()
cur.close()
conn.close()

print("Date dimension populated (2000–2030)")
