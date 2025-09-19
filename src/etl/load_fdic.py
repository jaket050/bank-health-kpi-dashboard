import pandas as pd
from sqlalchemy import create_engine

# Database connection settings
DB_USER = "postgres" 
DB_PASSWORD = "1234" 
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "bank_kpi"

# File path to my FDIC CSV
CSV_FILE = "data/raw/fdic_bank_summary.csv"

def load_fdic_data():
    #  Read the CSV into pandas
    df = pd.read_csv(CSV_FILE)

    #  Rename columns to match staging table
    df = df.rename(columns={
        "ASSET": "total_assets",
        "BANKS": "num_banks",
        "DEP": "total_deposits",
        "EQNM": "total_equity",
        "ID": "report_id",
        "NETINC": "net_income",
        "STNAME": "country_name",
        "YEAR": "report_year"
    })

    #  Connect to PostgreSQL
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Load dataframe into staging table
    df.to_sql("staging_fdic", engine, if_exists="replace", index=False)

    print("FDIC data loaded successfully into staging_fdic")

if __name__ == "__main__":
    load_fdic_data()
