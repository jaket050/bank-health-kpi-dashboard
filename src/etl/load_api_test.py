import requests
import pandas as pd
import psycopg2
from configparser import ConfigParser

# Load config
config = ConfigParser()
config.read("/Users/mac/Desktop/Projects/bank-health-kpi-dashboard/config.ini")

api_key = config.get("fdic_api", "api_key")
base_url = config.get("fdic_api", "base_url")  # should now be https://api.fdic.gov/banks/financials

# Build parameters
params = {
    "filters": "CERT:0",  # Example: use actual bank cert or a broader filter
    "fields": "CERT,REPDTE,ASSET,DEP,EQ,NETINC",
    "limit": 1000,
    "sort_by": "REPDTE",
    "sort_order": "DESC",
    "api_key": api_key
}

# Make request
response = requests.get(base_url, params=params)
response.raise_for_status()
data = response.json()

# Normalize results (may vary structure)
df = pd.json_normalize(data.get("data", data.get("results", [])))

print("Sample DataFrame columns:", df.columns)
