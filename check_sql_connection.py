#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt do weryfikacji polaczenia z SQL Server i sprawdzenia tabel
"""

import pyodbc
import sys
from datetime import datetime

# Konfiguracja
SERVER = 'PF3L02RY'
DATABASE = 'BI_DW'
USERNAME = 'dlt_user'
PASSWORD = 'Lab5Pass!23'

def test_connection():
    """Test polaczenia z SQL Server"""
    try:
        # Try ODBC Driver 17 or 18
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Probuję połączyć się z {SERVER}\\{DATABASE}...")
        conn = pyodbc.connect(connection_string)
        print("[OK] Połączenie udane!")

        cursor = conn.cursor()

        # Sprawdz tabele
        print("\n[INFO] Sprawdzam tabele w schemacie [Extract]...\n")

        tables_to_check = [
            ('sales_order_header', 31465),
            ('sales_order_detail', 121317),
            ('CurrencyRateData', 1004),
        ]

        results = {}
        for table_name, expected_count in tables_to_check:
            query = f"SELECT COUNT(*) as cnt FROM [Extract].[{table_name}]"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            results[table_name] = count

            status = "OK" if count > 0 else "BLAD"
            print(f"[{status}] [{table_name}] - {count:,} wierszy (oczekiwane: {expected_count:,})")

        # Sprawdz kolumny w sales_order_header
        print("\n[INFO] Kolumny w [Extract].[sales_order_header]:")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'Extract' AND TABLE_NAME = 'sales_order_header'
            ORDER BY ORDINAL_POSITION
        """)
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")

        # Sprawdz kolumny w sales_order_detail
        print("\n[INFO] Kolumny w [Extract].[sales_order_detail]:")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'Extract' AND TABLE_NAME = 'sales_order_detail'
            ORDER BY ORDINAL_POSITION
        """)
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")

        # Sprawdz kolumny w CurrencyRateData
        print("\n[INFO] Kolumny w [Extract].[CurrencyRateData]:")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'Extract' AND TABLE_NAME = 'CurrencyRateData'
            ORDER BY ORDINAL_POSITION
        """)
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")

        print("\n[OK] Wszystkie tabele i kolumny dostepne!")
        print("[OK] Mozesz przystapic do tworzenia raportu Power BI\n")

        conn.close()
        return True

    except pyodbc.Error as e:
        print(f"[BLAD] Blad polaczenia: {e}")
        print("\n[INFO] Sprobuj:")
        print("  1. Sprawdz czy SQL Server dziala")
        print("  2. Sprawdz firewall")
        print("  3. Sprawdz haslo: Lab5Pass!23")
        print("  4. Sprawdz czy masz ODBC Driver zainstalowany")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
