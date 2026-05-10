"""
Lab5 - Prezentacja wyników ekstrakcji danych
"""
import pyodbc
from datetime import datetime

DST_CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=PF3L02RY;"
    "DATABASE=BI_DW;"
    "UID=dlt_user;"
    "PWD=Lab5Pass!23;"
    "TrustServerCertificate=yes;"
)

def show_results():
    conn = pyodbc.connect(DST_CONN_STR)
    cur = conn.cursor()

    print("\n" + "="*60)
    print("LAB5 - WYNIKI EKSTRAKCJI DANYCH")
    print("="*60)

    # 1. Tabele z AdventureWorks
    print("\n[1] TABELE Z ADVENTUREWORKS2014:")
    print("-" * 60)
    tables_data = [
        ('product', 'Produkty'),
        ('sales_order_header', 'Zaglowki zamowien'),
        ('sales_order_detail', 'Linie zamowien'),
        ('sales_person', 'Sprzedawcy'),
        ('sales_territory', 'Terytoria sprzedazy'),
        ('person', 'Osoby (kontakty)'),
        ('country_region', 'Kraje i regiony'),
    ]

    total_rows = 0
    for tbl, desc in tables_data:
        cur.execute(f'SELECT COUNT(*) FROM [extract].[{tbl}]')
        count = cur.fetchone()[0]
        total_rows += count
        print(f"  {desc:.<40} {count:>12} wierszy")

    print(f"  {'RAZEM':.<40} {total_rows:>12} wierszy")

    # 2. Przesunięcie dat
    print("\n[2] PRZESUNIĘCIE DAT ZAMÓWIEŃ (+11 lat):")
    print("-" * 60)
    cur.execute('''
        SELECT
          MIN(order_date) as Min_Date,
          MAX(order_date) as Max_Date,
          COUNT(*) as Liczba_zamowien
        FROM [extract].[sales_order_header]
    ''')
    row = cur.fetchone()
    print(f"  Od:               {row[0]}")
    print(f"  Do:               {row[1]}")
    print(f"  Liczba zamowien:  {row[2]} wierszy")

    # 3. Oceny produktów z CSV
    print("\n[3] OCENY PRODUKTÓW (plik CSV):")
    print("-" * 60)
    cur.execute('''
        SELECT
          COUNT(*) as Liczba_produktow,
          ROUND(AVG(AvgRating), 2) as Srednia_ocena,
          MIN(MinRating) as Min_ocena,
          MAX(MaxRating) as Max_ocena,
          SUM(ReviewCount) as Lacznie_opinii
        FROM [extract].[ProductRating]
    ''')
    row = cur.fetchone()
    print(f"  Produkty z ocenami: {row[0]} sztuk")
    print(f"  Średnia ocena:      {row[1]}")
    print(f"  Min ocena:          {row[2]}")
    print(f"  Max ocena:          {row[3]}")
    print(f"  Łącznie opinii:     {row[4]}")

    # 4. Kursy walut
    print("\n[4] KURSY WALUT (API NBP):")
    print("-" * 60)
    cur.execute('''
        SELECT
          COUNT(*) as Liczba_kursow,
          MIN(RateDate) as Poczatek,
          MAX(RateDate) as Koniec,
          ROUND(AVG(Rate), 4) as Srednia_kurs
        FROM [extract].[CurrencyRateData]
    ''')
    row = cur.fetchone()
    print(f"  Waluta:             USD")
    print(f"  Liczba kursów:      {row[0]} dni")
    print(f"  Od:                 {row[1]}")
    print(f"  Do:                 {row[2]}")
    print(f"  Średni kurs:        {row[3]}")

    # 5. Przykładowe dane
    print("\n[5] PRZYKŁADOWE DANE:")
    print("-" * 60)

    print("\n  Produkty (TOP 3):")
    cur.execute('SELECT TOP 3 product_id, name FROM [extract].[product] ORDER BY product_id')
    for row in cur.fetchall():
        print(f"    - {row[1]}")

    print("\n  Ostatnie zamówienia (TOP 3):")
    cur.execute('''
        SELECT TOP 3 sales_order_id, order_date, total_due
        FROM [extract].[sales_order_header]
        ORDER BY order_date DESC
    ''')
    for row in cur.fetchall():
        print(f"    - Zamówienie {row[0]}: {row[1].date()} (${row[2]:.2f})")

    print("\n  Kursy USD (ostatnie 5 dni):")
    cur.execute('''
        SELECT TOP 5 RateDate, Rate
        FROM [extract].[CurrencyRateData]
        ORDER BY RateDate DESC
    ''')
    for row in cur.fetchall():
        print(f"    - {row[0]}: {row[1]:.4f} PLN/USD")

    print("\n" + "="*60)
    print("WSZYSTKIE ZADANIA UKOŃCZONE SUKCESEM!")
    print("="*60 + "\n")

    conn.close()

if __name__ == "__main__":
    show_results()
