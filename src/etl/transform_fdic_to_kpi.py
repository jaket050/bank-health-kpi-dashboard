import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from configparser import ConfigParser

# Load config
config = ConfigParser()
config.read("/Users/mac/Desktop/Projects/bank-health-kpi-dashboard/config.ini")

DB_USER = config.get("postgresql", "user")
DB_PASSWORD = config.get("postgresql", "password")
DB_HOST = config.get("postgresql", "host")
DB_PORT = config.get("postgresql", "port")
DB_NAME = config.get("postgresql", "dbname")

def transform_fdic_to_kpi():
    # Connect to database
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Read staging_institutions
    inst_df = pd.read_sql("SELECT * FROM staging_fdic_bank", engine)

    # Read dimensions
    bank_dim = pd.read_sql("SELECT bank_id, cert FROM bank_dim", engine)
    date_dim = pd.read_sql("SELECT date_id, full_date FROM date_dim", engine)

    # KPI calculations
    inst_df['roa'] = np.where(
                    inst_df["asset"].astype(float).abs() > 0,
                    inst_df["netinc"].astype(float) / inst_df["asset"].astype(float),
                    np.nan)
    inst_df['roe'] = np.where(
                    inst_df["eq"].astype(float).abs() > 0,
                    inst_df["netinc"].astype(float) / inst_df["eq"].astype(float),
                    np.nan)
    inst_df['capital_ratio'] = np.where(
                    inst_df["asset"].astype(float).abs() > 0,
                    inst_df["eq"].astype(float) / inst_df["asset"].astype(float),
                    np.nan) 
    inst_df['nim'] = pd.to_numeric(inst_df["nimy"], errors='coerce')
    inst_df['npl_ratio'] = pd.to_numeric(inst_df['npl'], errors='coerce') / 100

    # Join with bank_dim
    df = inst_df.merge(bank_dim, on="cert", how="left")

    # Join with date_dim (using effdate as reporting date)
    df = df.merge(date_dim, left_on="repdte", right_on="full_date", how="left")

    # Select fact table columns
    kpi_df = df[['bank_id','date_id','nim','roa','roe','npl_ratio','capital_ratio']]

    # Truncate fact table before loading
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE bank_kpi_fact;"))

    # Load into fact table
    kpi_df.to_sql('bank_kpi_fact', engine, if_exists='append', index=False)

    print(f"{len(kpi_df)}KPI rows loaded into bank_kpi_fact (table truncated before insert)")

if __name__ == "__main__":
    transform_fdic_to_kpi()

