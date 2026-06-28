# Sales & Profits Dashboard Build Guide

This guide recreates the supplied sample dashboard in Power BI using the project data.

## 1. Load Data

Load this file:

```text
powerbi/data/powerbi_vendor_dashboard.csv
```

Also load this file for the inventory KPI:

```text
powerbi/data/inventory_summary.csv
```

Then import the theme:

```text
powerbi/theme_blue_green.json
```

Create the DAX measures listed in `powerbi/dax_measures.md`.

## 2. Page Setup

- Page size: 16:9
- Canvas background: `#F7FAFC`
- Header height: about 80 px
- Left navigation width: about 150 px
- Main content starts after the left navigation

Use a dark navy header and sidebar:

- Header: `#06264A`
- Sidebar: `#052D4F`
- Accent teal: `#008C8C`
- Card border: `#D8E1E8`

## 3. Header

Add title:

```text
SALES & PROFITS DASHBOARD
Business Performance Overview
```

Add slicers on the right:

- Date Range: use a date field if you add a date dimension later. With current summary data, keep this as a placeholder or remove it.
- Category: use `Classification` only if you enrich the summary table with that field. Otherwise use Vendor or Brand slicer.

## 4. KPI Cards

Create four card visuals:

- Total Sales: `[Total Sales]`
- Total Purchase: `[Total Purchase]`
- Gross Profit: `[Gross Profit]`
- Unsold Capital: `[Unsold Capital]`

Recommended additions:

- Add `Profit Margin %` as a fifth KPI or tooltip.
- Calculate unsold capital from ending inventory value, not from purchase minus sales.
- Use green for positive performance and red for risk indicators.

## 5. Purchase Contribution Donut

Visual: Donut chart

- Legend: `VendorName`
- Values: `[Total Purchase]`
- Detail label: percentage of total
- Visual title: `PURCHASE CONTRIBUTION BY VENDOR`

Filter:

- Top N by `[Total Purchase]`, show top 6 vendors.
- Group smaller vendors as "Others" if you create a vendor grouping column.

## 6. Top 5 Vendors By Sales

Visual: Clustered bar chart

- Y-axis: `VendorName`
- X-axis: `[Total Sales]`
- Filter: Top 5 by `[Total Sales]`
- Sort: descending by `[Total Sales]`
- Title: `TOP 5 VENDORS BY TOTAL SALES`

## 7. Top 5 Brands By Sales

Visual: Clustered bar chart

- Y-axis: `Description`
- X-axis: `[Total Sales]`
- Filter: Top 5 by `[Total Sales]`
- Sort: descending by `[Total Sales]`
- Title: `TOP 5 BRANDS BY TOTAL SALES`

## 8. Lowest Inventory Turnover

Visual: Funnel chart or bar chart

- Group: `VendorName`
- Values: `[Stock Turnover]`
- Filter: Bottom 5 vendors by `[Stock Turnover]`
- Title: `TOP 5 VENDORS WITH LOWEST INVENTORY TURNOVER`

Business meaning:

Low turnover suggests slow-moving inventory, excess purchase volume, or weak sell-through.

## 9. Target Brands Scatter Plot

Visual: Scatter chart

- X-axis: `[Total Sales]`
- Y-axis: average `ProfitMargin` or `[Profit Margin %]`
- Details: `Description`
- Legend: target segment if using `target_brand_segments.csv`; otherwise use a calculated column
- Size: `[Gross Profit]`
- Title: `TARGET BRANDS (LOW SALES, HIGH PROFIT MARGIN)`

Suggested thresholds:

- Low sales: bottom 15th percentile of brand sales
- High margin: top 85th percentile of profit margin

## 10. Documentation Section

The sample has a bottom documentation row. For a professional Power BI report, use it as a second page named `Methodology`.

Recommended pages:

- Page 1: Executive Dashboard
- Page 2: Vendor Deep Dive
- Page 3: Brand Opportunities
- Page 4: Methodology

## 11. Final Dashboard Story

The dashboard should answer five business questions:

1. What is the current sales, purchase, profit, and inventory exposure?
2. Which vendors dominate purchasing and revenue?
3. Which brands generate the most sales?
4. Which vendors have inventory efficiency risk?
5. Which high-margin, low-sales brands should be targeted for growth?
