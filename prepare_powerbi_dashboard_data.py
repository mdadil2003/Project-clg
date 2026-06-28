from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
SOURCE_PATH = BASE_DIR / "outputs" / "vendor_sales_summary.csv"
END_INVENTORY_PATH = BASE_DIR / "Data" / "end_inventory.csv"
POWERBI_DIR = BASE_DIR / "powerbi"
EXPORT_DIR = POWERBI_DIR / "data"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def money_millions(value):
    return round(value / 1_000_000, 2)


def main():
    df = pd.read_csv(SOURCE_PATH)
    end_inventory = pd.read_csv(END_INVENTORY_PATH)
    end_inventory["UnsoldCapital"] = end_inventory["onHand"] * end_inventory["Price"]

    inventory_summary = (
        end_inventory.groupby(["Brand", "Description"], as_index=False)
        .agg(
            EndingInventoryUnits=("onHand", "sum"),
            UnsoldCapital=("UnsoldCapital", "sum"),
        )
    )
    inventory_summary.to_csv(EXPORT_DIR / "inventory_summary.csv", index=False)

    dashboard_df = df[
        (df["TotalSalesDollars"] > 0)
        & (df["GrossProfit"] > 0)
        & (df["ProfitMargin"] > 0)
    ].copy()

    dashboard_df = dashboard_df.merge(
        inventory_summary,
        on=["Brand", "Description"],
        how="left",
    )
    dashboard_df["EndingInventoryUnits"] = dashboard_df["EndingInventoryUnits"].fillna(0)
    dashboard_df["UnsoldCapital"] = dashboard_df["UnsoldCapital"].fillna(0)

    dashboard_df.to_csv(EXPORT_DIR / "powerbi_vendor_dashboard.csv", index=False)

    kpi = pd.DataFrame(
        [
            {
                "TotalSales": dashboard_df["TotalSalesDollars"].sum(),
                "TotalPurchase": dashboard_df["TotalPurchaseDollars"].sum(),
                "GrossProfit": dashboard_df["GrossProfit"].sum(),
                "UnsoldCapital": inventory_summary["UnsoldCapital"].sum(),
                "AverageProfitMargin": dashboard_df["ProfitMargin"].mean(),
                "AverageStockTurnover": dashboard_df["StockTurnover"].mean(),
                "VendorCount": dashboard_df["VendorName"].nunique(),
                "BrandCount": dashboard_df["Description"].nunique(),
                "TotalSalesMillions": money_millions(dashboard_df["TotalSalesDollars"].sum()),
                "TotalPurchaseMillions": money_millions(dashboard_df["TotalPurchaseDollars"].sum()),
                "GrossProfitMillions": money_millions(dashboard_df["GrossProfit"].sum()),
                "UnsoldCapitalMillions": money_millions(inventory_summary["UnsoldCapital"].sum()),
            }
        ]
    )
    kpi.to_csv(EXPORT_DIR / "kpi_summary.csv", index=False)

    vendor_summary = (
        dashboard_df.groupby("VendorName", as_index=False)
        .agg(
            TotalSalesDollars=("TotalSalesDollars", "sum"),
            TotalPurchaseDollars=("TotalPurchaseDollars", "sum"),
            GrossProfit=("GrossProfit", "sum"),
            ProfitMargin=("ProfitMargin", "mean"),
            StockTurnover=("StockTurnover", "mean"),
            UnsoldCapital=("UnsoldCapital", "sum"),
        )
        .sort_values("TotalSalesDollars", ascending=False)
    )
    vendor_summary["PurchaseContributionPct"] = (
        vendor_summary["TotalPurchaseDollars"]
        / vendor_summary["TotalPurchaseDollars"].sum()
        * 100
    )
    vendor_summary.to_csv(EXPORT_DIR / "vendor_summary.csv", index=False)
    vendor_summary.head(5).to_csv(EXPORT_DIR / "top_5_vendors_by_sales.csv", index=False)
    vendor_summary.sort_values("StockTurnover", ascending=True).head(5).to_csv(
        EXPORT_DIR / "lowest_5_inventory_turnover_vendors.csv", index=False
    )

    brand_summary = (
        dashboard_df.groupby("Description", as_index=False)
        .agg(
            TotalSalesDollars=("TotalSalesDollars", "sum"),
            GrossProfit=("GrossProfit", "sum"),
            ProfitMargin=("ProfitMargin", "mean"),
            StockTurnover=("StockTurnover", "mean"),
        )
        .sort_values("TotalSalesDollars", ascending=False)
    )
    brand_summary.to_csv(EXPORT_DIR / "brand_summary.csv", index=False)
    brand_summary.head(5).to_csv(EXPORT_DIR / "top_5_brands_by_sales.csv", index=False)

    low_sales_threshold = brand_summary["TotalSalesDollars"].quantile(0.15)
    high_margin_threshold = brand_summary["ProfitMargin"].quantile(0.85)
    brand_summary["TargetSegment"] = "Others"
    brand_summary.loc[
        (brand_summary["TotalSalesDollars"] <= low_sales_threshold)
        & (brand_summary["ProfitMargin"] >= high_margin_threshold),
        "TargetSegment",
    ] = "High Profit Margin Low Sales"
    brand_summary.loc[
        (brand_summary["TotalSalesDollars"] > low_sales_threshold)
        & (brand_summary["ProfitMargin"] >= high_margin_threshold),
        "TargetSegment",
    ] = "High Sales High Profit Margin"
    brand_summary.loc[
        (brand_summary["TotalSalesDollars"] <= low_sales_threshold)
        & (brand_summary["ProfitMargin"] < high_margin_threshold),
        "TargetSegment",
    ] = "Low Profit Margin Low Sales"
    brand_summary.to_csv(EXPORT_DIR / "target_brand_segments.csv", index=False)

    print(f"Power BI dashboard data exported to {EXPORT_DIR}")


if __name__ == "__main__":
    main()
