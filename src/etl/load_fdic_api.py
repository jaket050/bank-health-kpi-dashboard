import math, time, requests, pandas as pd
from configparser import ConfigParser
import psycopg2
from psycopg2.extras import execute_values

CONFIG_PATH = "/Users/mac/Desktop/Projects/bank-health-kpi-dashboard/config.ini"

def get_cfg():
    cfg = ConfigParser()
    cfg.read(CONFIG_PATH)
    return dict(cfg.items("postgresql")), dict(cfg.items("fdic"))

def get_conn(pg):
    return psycopg2.connect(
        host=pg["host"], port=pg["port"], dbname=pg["dbname"],
        user=pg["user"], password=pg["password"]
    )

def quarter_ends(years):
    q = ["0331","0630","0930","1231"]
    return [f"{y}{qq}" for y in years for qq in q]

def fetch_financials(api, years):
    base_url = api["base_url"].rstrip("/")
    api_key  = api.get("api_key", "")

    fields = ["CERT","NAMEFULL","REPDTE","ASSET","DEP","EQ","NETINC","STALP","CITY", "INTINC", "EINTEXP", "ERNASTR", "LNLSNET", "NIMY", "NPERFV"]
    all_rows, sess = [], requests.Session()

    for repdte in quarter_ends(years):
        params = {
            "filters": f"ACTIVE:1 AND !(BKCLASS:NC) AND REPDTE:{repdte}",
            "fields": ",".join(fields),
            "limit": 10000,
            "sort_by": "CERT",
            "format": "json",
            "api_key": api_key
        }
        r = sess.get(base_url, params=params, timeout=60)
        if r.status_code != 200:
            print(f"[WARN] HTTP {r.status_code} {r.url}\n{r.text[:300]}")
            continue

        payload = r.json()
        data = payload.get("data") or []
        if not data:
            print(f"[INFO] No rows for REPDTE={repdte}")
            continue

        # Flatten: rows may be under 'data' key
        if isinstance(data, list) and data and isinstance(data[0], dict):
            if "data" in data[0] and isinstance(data[0]["data"], dict):
                rows = [x["data"] for x in data]
            else:
                rows = data
        else:
            rows = []

        all_rows.extend(rows)

        total = payload.get("meta", {}).get("total") or 0
        # If API paginates, fetch more (rare in this query, but safe)
        if total > len(rows):
            pages = math.ceil((total - len(rows)) / params["limit"])
            for p in range(1, pages + 1):
                params["offset"] = p * params["limit"]
                rr = sess.get(base_url, params=params, timeout=60)
                dd = (rr.json().get("data") or [])
                if dd and "data" in dd[0] and isinstance(dd[0]["data"], dict):
                    dd = [x["data"] for x in dd]
                all_rows.extend(dd)
                time.sleep(0.15)

    if not all_rows:
        return pd.DataFrame()

    df = pd.json_normalize(all_rows)
    df.columns = [c.split(".")[-1].upper() for c in df.columns]
    for f in fields:
        if f not in df.columns:
            df[f] = None

    df = df.rename(columns={
        "CERT":"cert","NAMEFULL":"name","REPDTE":"repdte",
        "ASSET":"asset","DEP":"dep","EQ":"eq","NETINC":"netinc",
        "STALP":"state","CITY":"city", "INTINC":"intinc", "EINTEXP":"intexp", "ERNASTR":"earnasst", "LNLSNET":"loans", "NPERFV":"npl", "NIMY":"nimy"
    })

    for c in ["asset","dep","eq","netinc"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["repdte"] = pd.to_datetime(df["repdte"], format="%Y%m%d", errors="coerce").dt.date
    df = df.dropna(subset=["cert","repdte"]).drop_duplicates(subset=["cert","repdte"])

    return df

def upsert(conn, df):
    if df.empty:
        print("No rows to upsert.")
        return
    rows = list(df[["cert","name","repdte","asset","dep","eq","netinc","intinc","intexp","earnasst", "loans", "npl", "nimy", "state","city"]].itertuples(index=False))
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO staging_fdic_bank
              (cert,name,repdte,asset,dep,eq,netinc,intinc,intexp,earnasst,loans,npl,nimy,state,city)
            VALUES %s
            ON CONFLICT (cert, repdte) DO UPDATE SET
              name=EXCLUDED.name,
              asset=EXCLUDED.asset,
              dep=EXCLUDED.dep,
              eq=EXCLUDED.eq,
              netinc=EXCLUDED.netinc,
              intinc=EXCLUDED.intinc,
              intexp=EXCLUDED.intexp,
              earnasst=EXCLUDED.earnasst,
              loans=EXCLUDED.loans,
              npl=EXCLUDED.npl,
              nimy=EXCLUDED.nimy,                         
              state=EXCLUDED.state,
              city=EXCLUDED.city;
        """, rows)
    conn.commit()
    print(f"Upserted {len(rows)} rows into staging_fdic_bank")

if __name__ == "__main__":
    pg, api = get_cfg()
    conn = get_conn(pg)

    # Start with 2024 (works based on your quick_check)
    years = list(range(2019, 2025))

    df = fetch_financials(api, years)
    if df.empty:
        print("\nStill empty. Open this in your browser to verify you get rows:\n"
              "https://banks.data.fdic.gov/api/financials?filters=ACTIVE:1%20AND%20!(BKCLASS:NC)%20AND%20REPDTE:20241231&"
              "fields=CERT,NAMEFULL,REPDTE,ASSET,DEP,EQ,NETINC,STALP,CITY&limit=5&format=json\n")
    else:
        upsert(conn, df)
    conn.close()
