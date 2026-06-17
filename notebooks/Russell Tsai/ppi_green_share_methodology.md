# PPI Green Share — Cleaning and Classification Methodology

**Source data:** `data/raw/WB_PPI_2010-2024_energy.xlsx`, sheet `CustomQuery`
**Notebook:** `notebooks/Russell Tsai/01_ppi_cleaning.ipynb`
**Output files:** `data/clean/ppi_green_share.csv`, `data/clean/ppi_clean_project_level.csv`

---

## 1. Initial filters

Starting from 3,008 rows in the raw sheet, two filters were applied before classification:

1. **Subsector == 'Electricity'** — dropped 57 rows covering non-electricity energy subsectors (e.g. pipelines, water). Retained 2,951 rows.
2. **Technology not in {'Not Applicable', 'Other'} and not null** — dropped 252 rows where no meaningful technology was recorded. Retained 2,699 rows.

---

## 2. Green vs brown classification (`is_green`)

Each project was classified based on an exact match of the `Technology` string.

**Green (is_green = 1)**

| Technology values |
|---|
| Solar, PV · Solar, CSP · Solar, CPV |
| Solar, PV, N/A · Solar, PV, Not Applicable *(Solar with no meaningful secondary tech)* |
| Wind · Wind, N/A · Wind, Not Applicable *(Wind with no meaningful secondary tech)* |
| Wind, Solar, PV · Solar, PV, Wind · Solar, PV, Wind, N/A · Solar, PV, Solar, PV *(green-only combos)* |
| Solar, PV, Biogas *(green-only combo)* |
| Hydro, Small (<50MW) · Geothermal · Biomass · Biogas |

**Brown (is_green = 0)**

| Technology values |
|---|
| Coal · Natural Gas · Diesel · Steam |
| Natural Gas, Diesel · Diesel, Natural Gas · Natural Gas, Steam *(brown-only combos)* |

---

## 3. Ambiguous cases and the broad definition (`is_green_broad`)

Two technology categories were not automatically assigned to green or brown, and instead left as `NaN` in the primary `is_green` column:

- **Hydro, Large (>50MW)** (127 projects): Large hydropower carries contested environmental status — it provides carbon-free generation but is associated with significant ecological and social impacts. Automatic inclusion in green would overstate the green share in countries like Albania that have large hydro assets.
- **Waste** (65 projects): Waste-to-energy projects reduce landfill but combust organic material, making their carbon profile ambiguous.

To support a robustness check, a second column `is_green_broad` was created that is identical to `is_green` except these two categories are reclassified as green (1). This allows the main analysis to use the narrow definition while sensitivity tables can re-run with the broad definition.

**Six noisy hybrid rows** were left as `NaN` in both `is_green` and `is_green_broad` and excluded from all aggregations:

| Technology | Count |
|---|---|
| Wind, Coal, N/A | 1 |
| Solar, PV, Wind, Coal, N/A | 1 |
| Natural Gas, Steam, Solar, CSP | 1 |
| Natural Gas, Other | 1 |
| Solar, PV, Other | 1 |
| Wind, Other | 1 |

These represent genuine green–brown or green–ambiguous hybrids with no clean classification. At 6 rows total they are negligible in scale and dropping them avoids introducing noise into the numerator or denominator.

---

## 4. TotalInvestment conversion

`TotalInvestment` was stored as a mixed-type column containing numeric strings and the placeholder values `"Not Available"` (105 rows) and `"Not Applicable"` (1 row). These were coerced to `NaN` using `pd.to_numeric(..., errors='coerce')`, resulting in 106 missing values (3.9% of the 2,699-row dataset). No numeric information was lost in this step. Investment figures are in USD millions as reported by the World Bank PPI database.

---

## 5. Country-year aggregation

Projects were aggregated to the country × financial-closure-year level separately under each definition before merging.

**Narrow base** (for `is_green` columns): rows where `is_green` is `NaN` were dropped (198 rows: 127 Hydro Large + 65 Waste + 6 hybrids). Totals reflect only clearly classified projects.

**Broad base** (for `is_green_broad` columns): only the 6 hybrid rows were dropped. Hydro Large and Waste are included in both the numerator (when green) and the denominator. Broad and narrow totals therefore differ for country-years that contain these projects.

Metrics computed for each definition:

| Column | Definition |
|---|---|
| `total_investment` / `total_investment_broad` | Sum of TotalInvestment (USD M), NaN excluded |
| `total_projects` / `total_projects_broad` | Count of projects in the base |
| `green_investment` / `green_investment_broad` | Sum of TotalInvestment for green projects |
| `green_projects` / `green_projects_broad` | Count of green projects |
| `green_share_value` / `green_share_value_broad` | green_investment ÷ total_investment |
| `green_share_count` / `green_share_count_broad` | green_projects ÷ total_projects |

---

## 6. Output files

### `data/clean/ppi_green_share.csv`
Country-year panel. **556 rows × 14 columns.**

```
Country, Financial closure year,
total_investment, total_projects, green_investment, green_projects,
green_share_value, green_share_count,
total_investment_broad, total_projects_broad, green_investment_broad,
green_projects_broad, green_share_value_broad, green_share_count_broad
```

### `data/clean/ppi_clean_project_level.csv`
Project-level cleaned data. **2,699 rows × 48 columns.**

Original 45 raw columns from the World Bank PPI sheet, plus:

```
is_green          — 1 (green), 0 (brown), NaN (ambiguous) under narrow definition
ambiguous_flag    — 1 for rows where is_green is NaN
is_green_broad    — same as is_green but Hydro Large and Waste reclassified as 1
```
