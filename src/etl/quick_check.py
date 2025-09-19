import requests
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read("/Users/mac/Desktop/Projects/bank-health-kpi-dashboard/config.ini")
api_key = cfg.get("fdic", "api_key")
base_url = cfg.get("fdic", "base_url").rstrip("/")

params = {
    "filters": "REPDTE:20241231",
    "limit": 1,
    "format": "json",
    "api_key": api_key
}

r = requests.get(base_url, params=params, timeout=30)
r.raise_for_status()
payload = r.json()

import json
print(json.dumps(payload, indent=2))  # pretty print the whole response
