# Power BI DAX Measures

Create these measures in the main table loaded from `powerbi/data/powerbi_vendor_dashboard.csv`.
For the cleanest inventory KPI, also load `powerbi/data/inventory_summary.csv`.

```DAX
Total Sales = SUM(powerbi_vendor_dashboard[TotalSalesDollars])

Total Purchase = SUM(powerbi_vendor_dashboard[TotalPurchaseDollars])

Gross Profit = SUM(powerbi_vendor_dashboard[GrossProfit])

Unsold Capital = SUM(inventory_summary[UnsoldCapital])

Ending Inventory Units = SUM(inventory_summary[EndingInventoryUnits])

Profit Margin % =
DIVIDE([Gross Profit], [Total Sales], 0)

Stock Turnover =
DIVIDE(
    SUM(powerbi_vendor_dashboard[TotalSalesQuantity]),
    SUM(powerbi_vendor_dashboard[TotalPurchaseQuantity]),
    0
)

Sales To Purchase Ratio =
DIVIDE([Total Sales], [Total Purchase], 0)

Vendor Count = DISTINCTCOUNT(powerbi_vendor_dashboard[VendorName])

Brand Count = DISTINCTCOUNT(powerbi_vendor_dashboard[Description])

Purchase Contribution % =
DIVIDE(
    [Total Purchase],
    CALCULATE(
        [Total Purchase],
        ALL(powerbi_vendor_dashboard[VendorName])
    ),
    0
)

Top 5 Vendor Sales Rank =
RANKX(
    ALL(powerbi_vendor_dashboard[VendorName]),
    [Total Sales],
    ,
    DESC,
    Dense
)

Top 5 Brand Sales Rank =
RANKX(
    ALL(powerbi_vendor_dashboard[Description]),
    [Total Sales],
    ,
    DESC,
    Dense
)
```

Recommended formatting:

- Format `Total Sales`, `Total Purchase`, `Gross Profit`, and `Unsold Capital` as Currency with display units set to Millions.
- Format `Profit Margin %` and `Purchase Contribution %` as Percentage.
- Format `Stock Turnover` as Decimal Number with 2 decimals.
