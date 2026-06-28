# Dataset

Raw CSV files are not committed to GitHub because they are large.

Expected local files:

- `begin_inventory.csv`
- `end_inventory.csv`
- `purchase_prices.csv`
- `purchases.csv`
- `sales.csv`
- `vendor_invoice.csv`

Place these files in this `Data/` directory before running the pipeline:

```powershell
python ingestion_db.py
python get_vendor_summary.py
python ml_vendor_classification.py
python prepare_powerbi_dashboard_data.py
```

The repository includes generated summary outputs so reviewers can understand the project without downloading the full raw dataset.
