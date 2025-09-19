import pandas as pd
import psycopg2
from psycopg2 import sql
from configparser import ConfigParser

# Read DB config
config = ConfigParser()
config.read('/Users/mac/Desktop/Projects/bank-health-kpi-dashboard/config.ini')


db_params = {
    "host": config.get("postgresql", "host"),
    "port": config.get("postgresql", "port"),
    "dbname": config.get("postgresql", "dbname"),
    "user": config.get("postgresql", "user"),
    "password": config.get("postgresql", "password")
}

# Connect to DB
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Step 3: Read CSV
file_path = '/Users/mac/Desktop/Projects/bank-health-kpi-dashboard/data/raw/institutions.csv'
df = pd.read_csv(file_path, low_memory=False)

# Clean / Cast Columns
df['ACTIVE'] = df['ACTIVE'].apply(lambda x: True if x == 1 else False)
df['ASSET'] = pd.to_numeric(df['ASSET'], errors='coerce')
df['EFFDATE'] = pd.to_datetime(df['EFFDATE'], errors='coerce')
df['STNAME'] = df['STNAME'].str.strip().str.upper()
df['CITY'] = df['CITY'].str.strip()

# Insert into staging
staging_columns = ['CERT', 'ACTIVE', 'CITY', 'STNAME', 'ASSET', 'EFFDATE', 'ROA', 'ROE']
for index, row in df.iterrows():
    cur.execute(
        """
        INSERT INTO staging_institutions (cert, active, city, state, asset, effdate, roa, roe)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (cert) DO NOTHING
        """,
        (row['CERT'], row['ACTIVE'], row['CITY'], row['STNAME'], row['ASSET'], row['EFFDATE'], row['ROA'], row['ROE'])
    )

conn.commit()

# Transform → bank_dim
cur.execute("""
INSERT INTO bank_dim (cert, name, city, state, established_date)
SELECT cert, NAME, city, state, effdate
FROM staging_institutions
ON CONFLICT (cert) DO UPDATE
SET name = EXCLUDED.name,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    established_date = EXCLUDED.established_date;
""")

conn.commit()

# Indexing
cur.execute("CREATE INDEX IF NOT EXISTS idx_bank_dim_state ON bank_dim(state);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_bank_dim_city ON bank_dim(city);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_bank_dim_cert ON bank_dim(cert);")
conn.commit()

# Cleanup
cur.close()
conn.close()

print("Institutions ETL completed successfully!")

