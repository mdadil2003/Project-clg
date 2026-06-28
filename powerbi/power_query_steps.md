# Power Query Setup

Use this if you load the main generated CSV directly into Power BI.

Source file:

```text
powerbi/data/powerbi_vendor_dashboard.csv
```

Power Query M pattern:

```powerquery
let
    Source = Csv.Document(
        File.Contents("C:\Path\To\Project\powerbi\data\powerbi_vendor_dashboard.csv"),
        [Delimiter=",", Columns=21, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"VendorNumber", Int64.Type},
            {"VendorName", type text},
            {"Brand", Int64.Type},
            {"Description", type text},
            {"PurchasePrice", type number},
            {"ActualPrice", type number},
            {"Volume", type number},
            {"TotalPurchaseQuantity", Int64.Type},
            {"TotalPurchaseDollars", type number},
            {"TotalSalesQuantity", Int64.Type},
            {"TotalSalesDollars", type number},
            {"TotalSalesPrice", type number},
            {"TotalExciseTax", type number},
            {"FreightCost", type number},
            {"GrossProfit", type number},
            {"ProfitMargin", type number},
            {"StockTurnover", type number},
            {"SalesToPurchaseRatio", type number},
            {"EndingInventoryUnits", Int64.Type},
            {"UnsoldCapital", type number}
        }
    ),
    FilteredRows = Table.SelectRows(
        ChangedTypes,
        each [TotalSalesDollars] > 0 and [GrossProfit] > 0 and [ProfitMargin] > 0
    )
in
    FilteredRows
```

If you use the already prepared CSV, the final filter step is still useful as a safety check.
