# ye project ka core processing script hai.
'''
SQL queries run karta hai 
different tables ko join karta hai
data cleaning
new columns create karta hai:
GrossProfit
ProfitMargin
StockTurnover
SalesToPurchaseRatio
'''

import time
import sqlite3
from pathlib import Path

import pandas as pd
import logging
from ingestion_db import ingest_db


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "inventory.db"
SQL_PATH = BASE_DIR / "sql" / "vendor_sales_summary.sql"
LOG_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("get_vendor_summary")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler(LOG_DIR / "get_vendor_summary.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


def create_vendor_summary(conn):
    """Merge raw retail tables into a vendor and brand level summary."""
    if not SQL_PATH.exists():
        raise FileNotFoundError(f"SQL transformation file not found: {SQL_PATH}")

    sql = SQL_PATH.read_text(encoding="utf-8")
    return pd.read_sql_query(sql, conn)


def clean_data(df):
    """Clean the summary data and create business KPI columns."""
    df = df.copy()

    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

    df.fillna(0, inplace=True)

    for col in ["VendorName", "Description"]:
        df[col] = df[col].astype(str).str.strip()

    df["GrossProfit"] = df["TotalSalesDollars"] - df["TotalPurchaseDollars"]
    df["ProfitMargin"] = (
        df["GrossProfit"] / df["TotalSalesDollars"].replace(0, pd.NA)
    ).fillna(0) * 100
    df["StockTurnover"] = (
        df["TotalSalesQuantity"] / df["TotalPurchaseQuantity"].replace(0, pd.NA)
    ).fillna(0)
    df["SalesToPurchaseRatio"] = (
        df["TotalSalesDollars"] / df["TotalPurchaseDollars"].replace(0, pd.NA)
    ).fillna(0)

    return df


if __name__ == '__main__':
    start = time.time()

    with sqlite3.connect(DB_PATH) as conn:
        logger.info("Creating vendor summary table")
        summary_df = create_vendor_summary(conn)
        logger.info("Summary rows: %s", len(summary_df))

        logger.info("Cleaning and feature engineering data")
        clean_df = clean_data(summary_df)
        logger.info("Cleaned rows: %s", len(clean_df))

        logger.info("Ingesting vendor_sales_summary")
        ingest_db(clean_df, "vendor_sales_summary", conn)

        output_path = OUTPUT_DIR / "vendor_sales_summary.csv"
        clean_df.to_csv(output_path, index=False)
        logger.info("Exported dashboard-ready CSV to %s", output_path)

    elapsed = time.time() - start
    logger.info("Completed in %.2f seconds", elapsed)
    print(f"Execution Time: {elapsed:.2f} seconds")
