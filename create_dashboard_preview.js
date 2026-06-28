const fs = require("fs");
const path = require("path");

const baseDir = __dirname;
const dataDir = path.join(baseDir, "powerbi", "data");
const outputPath = path.join(baseDir, "powerbi", "dashboard_preview.svg");

function parseCsv(filePath) {
  const text = fs.readFileSync(filePath, "utf8").trim();
  const lines = text.split(/\r?\n/);
  const headers = lines.shift().split(",");
  return lines.map((line) => {
    const values = line.match(/(".*?"|[^",]+)(?=\s*,|\s*$)/g) || [];
    const row = {};
    headers.forEach((header, idx) => {
      row[header] = (values[idx] || "").replace(/^"|"$/g, "");
    });
    return row;
  });
}

function money(value) {
  const n = Number(value || 0);
  return `$${(n / 1_000_000).toFixed(2)}M`;
}

function num(value, digits = 2) {
  return Number(value || 0).toFixed(digits);
}

function esc(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

const kpi = parseCsv(path.join(dataDir, "kpi_summary.csv"))[0];
const topVendors = parseCsv(path.join(dataDir, "top_5_vendors_by_sales.csv"));
const topBrands = parseCsv(path.join(dataDir, "top_5_brands_by_sales.csv"));
const lowTurnover = parseCsv(path.join(dataDir, "lowest_5_inventory_turnover_vendors.csv"));
const targetSegments = parseCsv(path.join(dataDir, "target_brand_segments.csv")).slice(0, 140);
const vendorSummary = parseCsv(path.join(dataDir, "vendor_summary.csv")).slice(0, 6);

function card(x, title, value, color) {
  return `
  <rect x="${x}" y="92" width="260" height="92" rx="8" fill="#ffffff" stroke="#d8e1e8"/>
  <circle cx="${x + 48}" cy="138" r="34" fill="${color}"/>
  <text x="${x + 98}" y="122" font-size="14" fill="#111827">${title}</text>
  <text x="${x + 98}" y="158" font-size="30" font-weight="700" fill="#111827">${value}</text>`;
}

function barChart(x, y, width, height, title, rows, labelField, valueField, color) {
  const max = Math.max(...rows.map((r) => Number(r[valueField] || 0)));
  const bars = rows.map((r, i) => {
    const yy = y + 54 + i * 42;
    const barW = Math.max(5, (Number(r[valueField] || 0) / max) * (width - 190));
    const label = esc(r[labelField]).slice(0, 24);
    return `
      <text x="${x + 18}" y="${yy + 17}" font-size="13" fill="#111827">${label}</text>
      <rect x="${x + 145}" y="${yy}" width="${barW}" height="22" fill="${color}"/>
      <text x="${x + 153 + barW}" y="${yy + 17}" font-size="12" fill="#111827">${money(r[valueField])}</text>`;
  }).join("");
  return `
  <rect x="${x}" y="${y}" width="${width}" height="${height}" rx="8" fill="#ffffff" stroke="#d8e1e8"/>
  <text x="${x + 18}" y="${y + 28}" font-size="15" font-weight="700" fill="#08264a">${title}</text>
  ${bars}`;
}

function turnoverChart() {
  const x = 170, y = 500, width = 430, height = 230;
  const maxWidth = 260;
  const bars = lowTurnover.map((r, i) => {
    const w = maxWidth - i * 32;
    const yy = y + 50 + i * 33;
    return `
      <text x="${x + 20}" y="${yy + 18}" font-size="13" fill="#111827">${esc(r.VendorName).slice(0, 28)}</text>
      <polygon points="${x + 170},${yy} ${x + 170 + w},${yy} ${x + 154 + w},${yy + 26} ${x + 186},${yy + 26}" fill="#1abc9c" opacity="${1 - i * 0.1}"/>
      <text x="${x + 320}" y="${yy + 18}" font-size="12" fill="#111827">${num(r.StockTurnover)}</text>`;
  }).join("");
  return `
  <rect x="${x}" y="${y}" width="${width}" height="${height}" rx="8" fill="#ffffff" stroke="#d8e1e8"/>
  <text x="${x + 18}" y="${y + 28}" font-size="15" font-weight="700" fill="#08264a">LOWEST INVENTORY TURNOVER</text>
  ${bars}`;
}

function donut() {
  const x = 170, y = 208;
  const colors = ["#005a9c", "#008c8c", "#1abc9c", "#4ba564", "#f4b43f", "#a7a9ac"];
  const total = vendorSummary.reduce((s, r) => s + Number(r.TotalPurchaseDollars || 0), 0);
  let start = -90;
  const slices = vendorSummary.map((r, i) => {
    const pct = Number(r.TotalPurchaseDollars || 0) / total;
    const end = start + pct * 360;
    const large = end - start > 180 ? 1 : 0;
    const r1 = 92, r2 = 52, cx = x + 130, cy = y + 130;
    const p = (angle, radius) => {
      const rad = (angle * Math.PI) / 180;
      return [cx + radius * Math.cos(rad), cy + radius * Math.sin(rad)];
    };
    const [x1, y1] = p(start, r1);
    const [x2, y2] = p(end, r1);
    const [x3, y3] = p(end, r2);
    const [x4, y4] = p(start, r2);
    start = end;
    return `<path d="M ${x1} ${y1} A ${r1} ${r1} 0 ${large} 1 ${x2} ${y2} L ${x3} ${y3} A ${r2} ${r2} 0 ${large} 0 ${x4} ${y4} Z" fill="${colors[i]}"/>`;
  }).join("");
  const legend = vendorSummary.map((r, i) => `
    <circle cx="${x + 300}" cy="${y + 58 + i * 24}" r="5" fill="${colors[i]}"/>
    <text x="${x + 314}" y="${y + 63 + i * 24}" font-size="12" fill="#111827">${esc(r.VendorName).slice(0, 25)}</text>`).join("");
  return `
  <rect x="${x}" y="${y}" width="430" height="270" rx="8" fill="#ffffff" stroke="#d8e1e8"/>
  <text x="${x + 18}" y="${y + 28}" font-size="15" font-weight="700" fill="#08264a">PURCHASE CONTRIBUTION BY VENDOR</text>
  ${slices}
  <text x="${x + 95}" y="${y + 126}" font-size="13" fill="#111827">Total Purchase</text>
  <text x="${x + 88}" y="${y + 150}" font-size="20" font-weight="700" fill="#111827">${money(kpi.TotalPurchase)}</text>
  ${legend}`;
}

function scatter() {
  const x = 620, y = 500, width = 650, height = 230;
  const maxSales = Math.max(...targetSegments.map((r) => Number(r.TotalSalesDollars || 0)));
  const maxMargin = Math.max(...targetSegments.map((r) => Number(r.ProfitMargin || 0)));
  const points = targetSegments.map((r) => {
    const px = x + 60 + (Number(r.TotalSalesDollars || 0) / maxSales) * (width - 120);
    const py = y + height - 45 - (Number(r.ProfitMargin || 0) / maxMargin) * (height - 80);
    const color = r.TargetSegment === "High Profit Margin Low Sales"
      ? "#4ba564"
      : r.TargetSegment === "High Sales High Profit Margin"
        ? "#005a9c"
        : r.TargetSegment === "Low Profit Margin Low Sales"
          ? "#e76f61"
          : "#a7a9ac";
    return `<circle cx="${px}" cy="${py}" r="4" fill="${color}" opacity="0.78"/>`;
  }).join("");
  return `
  <rect x="${x}" y="${y}" width="${width}" height="${height}" rx="8" fill="#ffffff" stroke="#d8e1e8"/>
  <text x="${x + 18}" y="${y + 28}" font-size="15" font-weight="700" fill="#08264a">TARGET BRANDS (LOW SALES, HIGH PROFIT MARGIN)</text>
  <line x1="${x + 60}" y1="${y + height - 45}" x2="${x + width - 35}" y2="${y + height - 45}" stroke="#9ca3af"/>
  <line x1="${x + 60}" y1="${y + 45}" x2="${x + 60}" y2="${y + height - 45}" stroke="#9ca3af"/>
  ${points}
  <text x="${x + 255}" y="${y + height - 12}" font-size="12" fill="#111827">Total Sales</text>
  <text x="${x + 8}" y="${y + 120}" font-size="12" fill="#111827" transform="rotate(-90 ${x + 8},${y + 120})">Profit Margin</text>`;
}

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820">
<rect width="1400" height="820" fill="#f7fafc"/>
<rect x="0" y="0" width="1400" height="82" fill="#06264a"/>
<rect x="0" y="0" width="150" height="740" fill="#052d4f"/>
<text x="115" y="42" font-size="28" font-weight="700" fill="#ffffff">SALES &amp; PROFITS DASHBOARD</text>
<text x="115" y="65" font-size="16" fill="#e5edf5">Business Performance Overview</text>
<rect x="14" y="110" width="122" height="50" rx="7" fill="#13b6a6"/>
<text x="54" y="141" font-size="15" font-weight="700" fill="#ffffff">Overview</text>
<text x="30" y="215" font-size="15" fill="#ffffff">Vendors</text>
<text x="30" y="285" font-size="15" fill="#ffffff">Brands</text>
<text x="30" y="355" font-size="15" fill="#ffffff">Inventory</text>
<text x="30" y="425" font-size="15" fill="#ffffff">Insights</text>
${card(170, "TOTAL SALES", money(kpi.TotalSales), "#4ba564")}
${card(445, "TOTAL PURCHASE", money(kpi.TotalPurchase), "#008c8c")}
${card(720, "GROSS PROFIT", money(kpi.GrossProfit), "#1abc9c")}
${card(995, "UNSOLD CAPITAL", money(kpi.UnsoldCapital), "#2563eb")}
${donut()}
${barChart(620, 208, 320, 270, "TOP 5 VENDORS BY TOTAL SALES", topVendors, "VendorName", "TotalSalesDollars", "#008c8c")}
${barChart(955, 208, 315, 270, "TOP 5 BRANDS BY TOTAL SALES", topBrands, "Description", "TotalSalesDollars", "#005a9c")}
${turnoverChart()}
${scatter()}
<text x="170" y="780" font-size="14" fill="#334155">Power BI implementation pack: data, DAX measures, theme JSON, Power Query steps, and build guide are saved in the powerbi folder.</text>
</svg>`;

fs.writeFileSync(outputPath, svg, "utf8");
console.log(outputPath);
