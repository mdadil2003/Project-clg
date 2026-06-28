'''
is file me maine machine learning model apply kiya hai.”
kya kiya:
Random Forest model 
vendor classification 

output:
High Performance
Medium Performance
Low Performance

CSV file generate hui
Ye model business ko decision lene me help karta hai.
'''


import logging
import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "inventory.db"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("ml_vendor_classification")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler(LOG_DIR / "ml_vendor_classification.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


FEATURE_COLUMNS = [
    "ProfitMargin",
    "TotalSalesDollars",
    "TotalPurchaseDollars",
    "StockTurnover",
]


def assign_performance_label(row):
    """Create a business-rule target label for supervised classification."""
    if row["SalesRankPct"] >= 0.67 and row["ProfitRankPct"] >= 0.67:
        return "High Performance"
    if row["SalesRankPct"] <= 0.33 or row["ProfitRankPct"] <= 0.33:
        return "Low Performance"
    return "Medium Performance"


def load_vendor_summary(db_path=DB_PATH):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(
            """
            SELECT *
            FROM vendor_sales_summary
            WHERE TotalSalesDollars > 0
              AND TotalPurchaseDollars > 0
              AND GrossProfit > 0
              AND ProfitMargin > 0
            """,
            conn,
        )


def build_training_frame(df):
    # Ensure numeric columns are properly typed
    df = df.copy()
    df["ProfitMargin"] = pd.to_numeric(df["ProfitMargin"], errors="coerce").fillna(0)
    df["TotalSalesDollars"] = pd.to_numeric(df["TotalSalesDollars"], errors="coerce").fillna(0)
    df["TotalPurchaseDollars"] = pd.to_numeric(df["TotalPurchaseDollars"], errors="coerce").fillna(0)
    df["GrossProfit"] = pd.to_numeric(df["GrossProfit"], errors="coerce").fillna(0)
    df["TotalSalesQuantity"] = pd.to_numeric(df["TotalSalesQuantity"], errors="coerce").fillna(0)
    df["TotalPurchaseQuantity"] = pd.to_numeric(df["TotalPurchaseQuantity"], errors="coerce").fillna(0)

    vendor_df = (
        df.groupby(["VendorNumber", "VendorName"], as_index=False)
        .agg(
            TotalSalesDollars=("TotalSalesDollars", "sum"),
            TotalPurchaseDollars=("TotalPurchaseDollars", "sum"),
            GrossProfit=("GrossProfit", "sum"),
            TotalSalesQuantity=("TotalSalesQuantity", "sum"),
            TotalPurchaseQuantity=("TotalPurchaseQuantity", "sum"),
            AvgProfitMargin=("ProfitMargin", "mean"),
        )
    )

    vendor_df["ProfitMargin"] = (
        vendor_df["GrossProfit"] / vendor_df["TotalSalesDollars"].replace(0, pd.NA)
    ).fillna(0) * 100
    vendor_df["StockTurnover"] = (
        vendor_df["TotalSalesQuantity"]
        / vendor_df["TotalPurchaseQuantity"].replace(0, pd.NA)
    ).fillna(0)

    vendor_df["SalesRankPct"] = vendor_df["TotalSalesDollars"].rank(pct=True)
    vendor_df["ProfitRankPct"] = vendor_df["ProfitMargin"].rank(pct=True)
    vendor_df["VendorCategory"] = vendor_df.apply(assign_performance_label, axis=1)
    return vendor_df


def train_classifier(vendor_df):
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import classification_report
        from sklearn.model_selection import train_test_split
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "scikit-learn is required for ML classification. "
            "Install project dependencies with: pip install -r requirements.txt"
        ) from exc

    X = vendor_df[FEATURE_COLUMNS]
    y = vendor_df["VendorCategory"]

    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=stratify,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, zero_division=0)
    vendor_df["PredictedVendorCategory"] = model.predict(X)

    return model, vendor_df, report


def main():
    logger.info("Loading vendor_sales_summary")
    df = load_vendor_summary()
    logger.info("Loaded %s rows", len(df))

    vendor_df = build_training_frame(df)
    logger.info("Built vendor-level training frame with %s rows", len(vendor_df))

    model, scored_df, report = train_classifier(vendor_df)
    logger.info("Model trained: %s", model)
    logger.info("Classification report:\n%s", report)

    output_path = OUTPUT_DIR / "vendor_classification.csv"
    scored_df.to_csv(output_path, index=False)
    print(report)
    print(f"Saved scored vendor classifications to {output_path}")


if __name__ == "__main__":
    main()
