"""
Zadanie 2 – Ekstrakcja danych.

Kopiuje wybrane tabele z AdventureWorks2014 do schematu [Extract] w bazie BI_DW,
importuje oceny produktów z pliku CSV oraz kursy walut z API NBP.
"""
from datetime import date, timedelta
from pathlib import Path

import dlt
import pandas as pd
import pyodbc
import requests

from dlt.sources.sql_database import sql_database

# Patch dlt's MSSQL destination to omit port from the ODBC DSN so that SQL
# Server can be reached via shared memory / named pipes without TCP on 1433.
from dlt.destinations.impl.mssql import configuration as _mssql_cfg

_orig_odbc_dict = _mssql_cfg.MsSqlCredentials.get_odbc_dsn_dict

def _odbc_dict_no_port(self):
    d = _orig_odbc_dict(self)
    d["SERVER"] = self.host  # drop ,port
    return d

_mssql_cfg.MsSqlCredentials.get_odbc_dsn_dict = _odbc_dict_no_port

ROOT_DIR = Path(__file__).resolve().parent

SRC_CONN = (
    "mssql+pyodbc://dlt_user:Lab5Pass!23@PF3L02RY/AdventureWorks2014"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&TrustServerCertificate=yes"
)

DST_CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=PF3L02RY;"
    "DATABASE=BI_DW;"
    "UID=dlt_user;"
    "PWD=Lab5Pass!23;"
    "TrustServerCertificate=yes;"
)


def get_conn() -> pyodbc.Connection:
    return pyodbc.connect(DST_CONN_STR)


def ensure_schema(conn: pyodbc.Connection, schema: str) -> None:
    cur = conn.cursor()
    cur.execute(
        f"IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name='{schema}') "
        f"EXEC('CREATE SCHEMA [{schema}]')"
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Zadanie 2.1 – dlt: tabele z AdventureWorks -> [Extract] w BI_DW
# ---------------------------------------------------------------------------

def run_extract() -> None:
    src_production = sql_database(SRC_CONN, schema="Production").with_resources(
        "Product", "ProductSubcategory", "ProductCategory"
    )
    src_sales = sql_database(SRC_CONN, schema="Sales").with_resources(
        "SalesPerson", "SalesTerritory", "SalesOrderHeader", "SalesOrderDetail"
    )
    src_person = sql_database(SRC_CONN, schema="Person").with_resources(
        "Person", "CountryRegion"
    )

    pipeline = dlt.pipeline(
        pipeline_name="aw_to_extract",
        destination="mssql",
        dataset_name="Extract",
    )

    for src in [src_production, src_sales, src_person]:
        info = pipeline.run(src, write_disposition="replace")
        print(info)


# ---------------------------------------------------------------------------
# Zadanie 2.2 – Przesuń daty zamówień o +11 lat (2011-2014 -> 2022-2025)
# ---------------------------------------------------------------------------

def shift_order_dates(years: int = 11) -> None:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(f"""
            IF OBJECT_ID('[Extract].[sales_order_header]', 'U') IS NOT NULL
            BEGIN
                UPDATE [Extract].[sales_order_header]
                SET order_date      = DATEADD(year, {years}, order_date),
                    ship_date       = DATEADD(year, {years}, ship_date),
                    due_date        = DATEADD(year, {years}, due_date),
                    modified_date   = DATEADD(year, {years}, modified_date)
                WHERE order_date IS NOT NULL;
            END
        """)
        conn.commit()
        print("Order dates shifted by", years, "years.")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Zadanie 2.2 – CSV: oceny produktów -> [Extract].[ProductRating]
# ---------------------------------------------------------------------------

def load_product_ratings(csv_path: str = "SBI2526-LAB-Rating-FixedDate.csv") -> None:
    df = pd.read_csv(csv_path)
    agg = (
        df.groupby("productid")
        .agg(
            AvgRating=("ratingOverall", "mean"),
            MinRating=("ratingOverall", "min"),
            MaxRating=("ratingOverall", "max"),
            ReviewCount=("reviewid", "count"),
        )
        .reset_index()
    )

    conn = get_conn()
    try:
        ensure_schema(conn, "Extract")
        cur = conn.cursor()
        cur.execute("""
            IF OBJECT_ID('[Extract].[ProductRating]', 'U') IS NOT NULL
                DROP TABLE [Extract].[ProductRating];
            CREATE TABLE [Extract].[ProductRating] (
                ProductID   INT,
                AvgRating   FLOAT,
                MinRating   FLOAT,
                MaxRating   FLOAT,
                ReviewCount INT
            );
        """)
        rows = [
            (int(r.productid), float(r.AvgRating), float(r.MinRating),
             float(r.MaxRating), int(r.ReviewCount))
            for _, r in agg.iterrows()
        ]
        cur.executemany(
            "INSERT INTO [Extract].[ProductRating] VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
        print(f"ProductRating loaded: {len(rows)} rows.")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Zadanie 2.3 – API NBP: kursy walut -> [Extract].[CurrencyRateData]
# ---------------------------------------------------------------------------

def get_rates(currency: str, days: int) -> pd.DataFrame:
    """Pobiera średni kurs waluty z API NBP za ostatnie `days` dni."""
    end = date.today()
    start = end - timedelta(days=days)
    rows: list[dict] = []
    window = 365
    cur_start = start
    while cur_start < end:
        cur_end = min(cur_start + timedelta(days=window - 1), end)
        url = (
            f"https://api.nbp.pl/api/exchangerates/rates/A/"
            f"{currency}/{cur_start}/{cur_end}/?format=json"
        )
        resp = requests.get(url, timeout=30)
        if resp.status_code == 404:
            cur_start = cur_end + timedelta(days=1)
            continue
        resp.raise_for_status()
        for r in resp.json().get("rates", []):
            rows.append({"Date": r["effectiveDate"], "Currency": currency, "Rate": r["mid"]})
        cur_start = cur_end + timedelta(days=1)
    return pd.DataFrame(rows)


def load_currency_rates(currency: str = "USD", days: int = 1460) -> None:
    df = get_rates(currency, days)

    conn = get_conn()
    try:
        ensure_schema(conn, "Extract")
        cur = conn.cursor()
        cur.execute("""
            IF OBJECT_ID('[Extract].[CurrencyRateData]', 'U') IS NOT NULL
                DROP TABLE [Extract].[CurrencyRateData];
            CREATE TABLE [Extract].[CurrencyRateData] (
                RateDate  DATE,
                Currency  VARCHAR(3),
                Rate      FLOAT
            );
        """)
        rows = [(r["Date"], r["Currency"], float(r["Rate"])) for _, r in df.iterrows()]
        cur.executemany(
            "INSERT INTO [Extract].[CurrencyRateData] VALUES (?, ?, ?)",
            rows,
        )
        conn.commit()
        print(f"CurrencyRateData loaded: {len(rows)} rows.")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Uruchomienie wszystkich kroków
# ---------------------------------------------------------------------------

def run_all() -> None:
    print("=== Krok 1: Ekstrakcja tabel z AdventureWorks (dlt) ===")
    run_extract()
    print("=== Krok 2: Przesunięcie dat zamówień o +11 lat ===")
    shift_order_dates(years=11)
    print("=== Krok 3: Ładowanie ocen produktów z CSV ===")
    load_product_ratings(csv_path=str(ROOT_DIR / "SBI2526-LAB-Rating-FixedDate.csv"))
    print("=== Krok 4: Ładowanie kursów walut z API NBP ===")
    load_currency_rates(currency="USD", days=1460)
    print("=== Ekstrakcja zakończona ===")


if __name__ == "__main__":
    run_all()
