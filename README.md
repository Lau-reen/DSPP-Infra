# DSPP-Infra
# Carbon Pricing and Energy Investment

## 👥 Team Members

* Laureen Attolou (@lau-reen) - Role/Responsibility
* Russell Li Tsai (@russelltsai-source) - Role/Responsibility
* Shota Emoto (@emtn44) - Role/Responsibility

---

## ❓ Research Question & 🎯 Hypothesis

### ❓ Domestic Policy Impact
* Does the implementation of domestic carbon pricing mechanisms (carbon taxes or Emissions Trading Systems - ETS) by a host country correlate with a statistically significant increase in the proportion of private investment directed toward resilient infrastructure projects?  
*Data note:* We will extract policy implementation years, scope, and effective price rates per metric ton of $\text{CO}_2$ equivalent.

### ❓ Transnational / Cross-Border Spillover Effects
* To what extent do high carbon prices or strict compliance mechanisms in an institutional investor's home country (e.g., the EU's Carbon Border Adjustment Mechanism [CBAM] or high domestic ETS price signals) influence their "green-to-brown" infrastructure investment ratio within emerging market project pipelines?

### ❓ Moderating Variables
* How do global and local macroeconomic uncertainties, as measured by the World Uncertainty Index (WUI), affect the transmission mechanism between carbon pricing policies and actual private capital mobilization?

---

## 📁 Data Sources

| Source | Description | URL |
| :--- | :--- | :--- |
| World Bank PPI Energy Dataset | Public-Private Infrastructure (PPI) Energy projects data, 2010-2024 | [World Bank PPI Database](https://ppi.worldbank.org/) |
| World Bank Carbon Pricing Dashboard | Data on carbon pricing initiatives, up to 2024 | [World Bank Carbon Pricing Dashboard](https://carbonpricingdashboard.worldbank.org/) |

### Data Sources Details


**MAIN - D.1 World Bank PPI Database**
*   **Variables**: project_id, country, year, total_investment, sector, technology, investor_origin_country
*   **Granularity**: Project-level, annual data by Country

_AUXILIARY (?)_

**D.2 World Bank Carbon Pricing Dashboard**
*   **Variables**: jurisdiction, policy_type (Tax, ETS), start_year, sector_coverage, effective_price
*   **Granularity**: National-level policy data by Jurisdiction and Year

**D.3 IMF Climate Change Indicators Dashboard**
*   **Variables**: country, year, GHG_emissions_intensity, carbon_footprint, climate_risk_vulnerability
*   **Granularity**: Annual data by Country

**D.4 World Uncertainty Index (WUI)**
*   **Variables**: country, year, WUI_index
*   **Granularity**: High-frequency (e.g., quarterly, annual) data by Country

**D.5 IEA/IRENA Policies and Measures Database**
*   **Variables**: country, year, policy_name, policy_type, description (for specific incentives/exemptions)
*   **Granularity**: Policy-level data by Country and Year

## 📁 Folder Structure

### Folder Structure Notes

* All projects **MUST** follow this standardized folder structure
* `data/raw/` - **NEVER** edit manually; store original data here
* `data/clean/` - Cleaned datasets ready for analysis
* `data/temp/` - Temporary files (can be deleted)
* `notebooks/` - Jupyter notebooks for analysis
* `src/` - Python code
* `reports/` - Final outputs: plots, summaries, model files
* `docs/` - Project documentation, README, presentations

### Folder Structure Tree

```text
project/
├── data/
│   ├── raw/                # Original, immutable data
│   │   ├── world_bank_raw.csv
│   │   └── imf_financials_raw.csv
│   ├── clean/              # Cleaned, transformed data
│   │   ├── world_bank_clean.csv
│   │   └── imf_merged_clean.csv
│   └── temp/               # Temporary working files
├── notebooks/              # Jupyter notebooks for exploration
│   ├── 01_eda_worldbank.ipynb
│   ├── 02_regression_analysis.ipynb
│   └── 03_policy_simulations.ipynb
├── src/                    # Production-ready scripts
│   ├── download_worldbank.py # API/Scraping script
│   ├── clean_data.py       # Merging and cleaning logic
│   └── visualize_worldbank.py # Chart generation functions
├── reports/                # Final outputs
│   ├── figures/            # Saved .png plots for the memo
│   │   ├── gdp_trend_line.png
│   │   └── debt_distribution.png
│   ├── policy_memo_final.pdf
│   └── regression_results.txt
└── docs/                   # Documentation
    ├── data_details.md     # Data dictionary & column definitions
    ├── data_architecture.md # Pipeline logic and join keys
    └── policy_context.md   # Political background & stakeholders
```

### 🔗 References
* Link to methodology references (see proposal)
