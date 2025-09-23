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
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Read staging data
    inst_df = pd.read_sql("SELECT * FROM staging_fdic_bank", engine)

    # Dimensions
    bank_dim = pd.read_sql("SELECT bank_id, cert FROM bank_dim", engine)
    date_dim = pd.read_sql("SELECT date_id, full_date FROM date_dim", engine)

    # KPI calculations
    inst_df['roa'] = np.where(inst_df["asset"].astype(float) > 0,
                              inst_df["netinc"].astype(float) / inst_df["asset"].astype(float), np.nan)
    inst_df['roe'] = np.where(inst_df["eq"].astype(float) > 0,
                              inst_df["netinc"].astype(float) / inst_df["eq"].astype(float), np.nan)
    inst_df['capital_ratio'] = np.where(inst_df["asset"].astype(float) > 0,
                                        inst_df["eq"].astype(float) / inst_df["asset"].astype(float), np.nan)
    inst_df['nim'] = pd.to_numeric(inst_df["nimy"], errors='coerce')
    inst_df['npl_ratio'] = pd.to_numeric(inst_df['npl'], errors='coerce') / 100

    # Join with dimensions
    df = inst_df.merge(bank_dim, on="cert", how="left") \
                .merge(date_dim, left_on="repdte", right_on="full_date", how="left")

    # Final fact table structure
    kpi_df = df[['bank_id','date_id','nim','roa','roe','npl_ratio','capital_ratio']]
    kpi_df['date_id'] = pd.to_datetime(kpi_df['date_id'].astype(str), format='%Y%m%d')

    UPSERT_SQL = text("""
    INSERT INTO public.bank_kpi_fact (bank_id, date_id, roa, roe, capital_ratio, nim, npl_ratio)
    VALUES (:bank_id, :date_id, :roa, :roe, :capital_ratio, :nim, :npl_ratio)
    ON CONFLICT (bank_id, date_id) DO UPDATE
    SET roa = EXCLUDED.roa,
        roe = EXCLUDED.roe,
        capital_ratio = EXCLUDED.capital_ratio,
        nim = EXCLUDED.nim,
        npl_ratio = EXCLUDED.npl_ratio;
    """)

    rows = len(kpi_df)
    chunk_size = 5000

    with engine.begin() as conn:
        before = conn.execute(text("SELECT COUNT(*) FROM bank_kpi_fact")).scalar()
        for chunk in np.array_split(kpi_df, max(1, int(np.ceil(rows / chunk_size)))):
            conn.execute(UPSERT_SQL, chunk.to_dict(orient="records"))
        after = conn.execute(text("SELECT COUNT(*) FROM bank_kpi_fact")).scalar()

    print(f"{rows} rows processed | {after - before} new/updated in bank_kpi_fact")


