# Vendor Performance Analysis & Retail Insight System

This project transforms raw retail transaction data into vendor, brand, profitability, and inventory insights. It combines Python, SQLite, SQL transformations, statistical analysis, machine learning, and Power BI reporting.

## Business Objective

Retail teams need to understand which vendors drive revenue, which vendors create profit risk, where inventory is moving slowly, and which brands deserve promotional attention. This system creates a repeatable analytics pipeline that supports procurement, pricing, inventory, and vendor relationship decisions.

## Architecture

```text
CSV source files
  -> Python ingestion
  -> SQLite raw tables
  -> SQL transformation CTEs
  -> vendor_sales_summary table
  -> Python KPI engineering and analysis
  -> ML vendor classification
  -> Power BI dashboard and business report
```

## Project Structure

```text
Data/                              Raw CSV files
Data/README.md                     Dataset description; raw data is not committed
logs/                              Execution logs
outputs/                           Generated analytical outputs
sql/vendor_sales_summary.sql        SQL transformation query
ingestion_db.py                     CSV-to-SQLite ingestion script
get_vendor_summary.py               Summary table generation script
ml_vendor_classification.py         Random Forest vendor classifier
Exploratory Data Analysis.ipynb      EDA and transformation notebook
Vendor Performance Analysis.ipynb    Business analysis notebook
inventory.db                        SQLite database
```

## GitHub Repository Notes

Large raw files are intentionally excluded from GitHub:

- `inventory.db`
- raw CSV files inside `Data/`
- logs, cache files, and IDE settings

The repository keeps the Python pipeline, notebooks, Power BI documentation, dashboard assets, and generated summary CSV outputs so reviewers can understand the project without downloading the full dataset.

Recommended files for review:

- `README.md`
- `ingestion_db.py`
- `get_vendor_summary.py`
- `ml_vendor_classification.py`
- `prepare_powerbi_dashboard_data.py`
- `Vendor Performance Analysis.ipynb`
- `Exploratory Data Analysis.ipynb`
- `outputs/vendor_sales_summary.csv`
- `outputs/vendor_classification.csv`
- `powerbi/dashboard_build_guide.md`
- `powerbi/dax_measures.md`
- `powerbi/data/kpi_summary.csv`

## Pipeline

1. `ingestion_db.py` loads all CSV files from `Data/` into `inventory.db`.
2. `get_vendor_summary.py` runs `sql/vendor_sales_summary.sql`, cleans the result, creates KPIs, stores `vendor_sales_summary`, and exports a dashboard-ready CSV.
3. The notebooks perform exploratory analysis, visualizations, statistical testing, and business interpretation.
4. `ml_vendor_classification.py` aggregates vendor-level features and classifies vendors as High, Medium, or Low Performance.
5. Power BI consumes the final CSV/table for executive dashboard reporting.

## Key KPIs

- `GrossProfit = TotalSalesDollars - TotalPurchaseDollars`
- `ProfitMargin = GrossProfit / TotalSalesDollars * 100`
- `StockTurnover = TotalSalesQuantity / TotalPurchaseQuantity`
- `SalesToPurchaseRatio = TotalSalesDollars / TotalPurchaseDollars`
- `UnsoldCapital = TotalPurchaseDollars - TotalSalesDollars` where applicable for dashboard-level inventory exposure

## Power BI Dashboard

The dashboard focuses on executive decision-making:

- KPI cards for Total Sales, Total Purchase, Gross Profit, and Unsold Capital
- Donut chart for purchase contribution by vendor
- Bar charts for top vendors and brands by sales
- Funnel chart for vendors with the lowest inventory turnover
- Scatter plot for low-sales, high-margin target brands
- Date range and category slicers for interactive filtering

## Run Order

```powershell
python ingestion_db.py
python get_vendor_summary.py
python ml_vendor_classification.py
```

If Python dependencies are missing:

```powershell
pip install -r requirements.txt
```

## Business Insights

- A small group of vendors contributes most of the revenue, confirming vendor concentration risk.
- Bulk purchasing can reduce unit cost, but it must be balanced against slow inventory turnover.
- Some brands have high profit margins but low sales volume, making them strong candidates for promotions.
- Vendors differ meaningfully in profitability and turnover, so procurement strategy should be segmented.
- ML classification creates a scalable first pass for vendor prioritization.

## Limitations

- The current system uses static CSV extracts rather than real-time ingestion.
- The first ML version uses rule-derived labels, so it should be validated against business-owned vendor categories.
- Power BI refresh is file/database driven and not yet automated through a cloud service.

## Future Enhancements

- Add data quality checks before ingestion.
- Add dimensional modeling with fact and dimension tables.
- Track vendor performance trends by month or quarter.
- Add demand forecasting and inventory reorder recommendations.
- Deploy the pipeline to a cloud warehouse and automate Power BI refresh.
