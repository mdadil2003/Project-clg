# Ye file data ingestion ke liye hai.
# kya karta hai: CSV files read karta hai & SQLite database me insert karta hai
# why: Raw data ko structured database me convert karne ke liye.

import logging
from pathlib import Path
import time
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"
DB_PATH = BASE_DIR / "inventory.db"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("ingestion_db")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler(LOG_DIR / "ingestion_db.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


def ingest_db(df, table_name, conn):
    """Load a dataframe into a SQLite table."""
    df.to_sql(table_name, con=conn, if_exists="replace", index=False)


def load_raw_data(data_dir=DATA_DIR, db_path=DB_PATH):
    """Load all CSV files from the data directory into SQLite."""
    start = time.time()

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    csv_files = sorted(data_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in: {data_dir}")

    with sqlite3.connect(db_path) as conn:
        for file_path in csv_files:
            df = pd.read_csv(file_path)
            table_name = file_path.stem
            logger.info("Ingesting %s into table %s", file_path.name, table_name)
            ingest_db(df, table_name, conn)
            logger.info("Loaded %s rows into %s", len(df), table_name)

    total_time = (time.time() - start) / 60
    logger.info("--------------Ingestion Complete--------------")
    logger.info("Total Time Taken: %.2f minutes", total_time)


if __name__ == '__main__':
    load_raw_data()
