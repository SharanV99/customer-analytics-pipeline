"""
load_data.py
Loads the UCI Online Retail II dataset into a DuckDB database.

Usage:
    1. Download 'online_retail_II.xlsx' from
       https://archive.ics.uci.edu/dataset/502/online+retail+ii
    2. Place it in the data/ folder
    3. Run: python load_data.py
"""

import pandas as pd
import duckdb

EXCEL_PATH = "data/online_retail_II.xlsx"
CSV_PATH = "data/online_retail.csv"
DB_PATH = "retail.duckdb"

def main():
    # Read and combine both sheets (2009-2010 and 2010-2011)
    print("Reading Excel sheets...")
    xls = pd.ExcelFile(EXCEL_PATH)
    df = pd.concat(
        [pd.read_excel(xls, sheet) for sheet in xls.sheet_names],
        ignore_index=True,
    )
    print(f"Combined shape: {df.shape}")

    # Save a CSV copy (faster for DuckDB to read)
    df.to_csv(CSV_PATH, index=False)
    print(f"Wrote {CSV_PATH}")

    # Load into DuckDB as raw_retail
    print("Loading into DuckDB...")
    con = duckdb.connect(DB_PATH)
    con.execute("DROP TABLE IF EXISTS raw_retail")
    con.execute(
        f"CREATE TABLE raw_retail AS SELECT * FROM read_csv_auto('{CSV_PATH}')"
    )
    row_count = con.execute("SELECT COUNT(*) FROM raw_retail").fetchone()[0]
    con.close()
    print(f"Done. raw_retail has {row_count:,} rows.")

if __name__ == "__main__":
    main()