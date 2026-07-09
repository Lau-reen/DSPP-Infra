# DSPP-Infra
# Climate policy and Energy Investment

## 👥 Team Members

* Laureen Attolou (@lau-reen) - CPDB data analysis, cleaning, classification
* Russell Li Tsai (@russelltsai-source) - PPI data processing and investment analysis
* Shota Emoto (@emtn44) - Regression analysis, visualization, and reporting

---

## ❓ Research Question & 🎯 Hypothesis

### ❓ Domestic Policy Impact
* Does the presence and breadth of domestic clean-energy and resilience policies correlate with a higher level of private investment in green or resilient infrastructure projects?
* We examine both the absolute number of relevant policies and the share of green policies within a country’s broader climate policy portfolio, using a two-year lag between policy adoption and investment outcomes.

### ❓ Moderating Variables
* How do country GDP, rule of law affect the translation of policy adoption into actual investment deployment?

---

## 📁 Data Sources

| Source | Description | Use in the project |
| :--- | :--- | :--- |
| World Bank PPI Energy Dataset | Private infrastructure project investment data, 2010–2024 | Measures green and total energy investment outcomes |
| Climate Policy Database (CPDB) | National climate and policy records | Identifies relevant policies and policy counts |
| Mentges Enhanced Climate Resilience Taxonomy | Structured taxonomy of resilience-related policy terms | Supports resilience-policy classification (not used in final version)|
| World Bank Worldwide Governance Indicators | Rule of Law| Provides supplementary policy context |
| World Bank World Development Indicator | GDP | Provides supplementary policy context |

### Data Sources Details

**Main - World Bank PPI Database**
* Variables: project-level investment, country, year, technology, and project type
* Granularity: Project-level data by country and year

**Main - Climate Policy Database**
* Variables: policy descriptions, jurisdiction, status, dates, and policy classification fields
* Granularity: Policy-level data by country and year

---

## 📁 Folder Structure

### Folder Structure Notes

* data/raw/ - Original source files and immutable inputs
* data/clean/ - Cleaned datasets ready for analysis
* data/temp/ - Intermediate and temporary files
* notebooks/ - Jupyter notebooks for exploration and analysis
* src/ - Python scripts for cleaning, analysis, and reporting
* reports/ - Final outputs, plots, and summary files
* docs/ - Project documentation and report drafts

### Folder Structure Tree

```text
DSPP-Infra/
├── data/
│   ├── raw/                # Original datasets
│   ├── clean/              # Cleaned analysis files
│   └── temp/               # Temporary outputs
├── notebooks/              # Analysis notebooks
├── src/                    # Python scripts
├── reports/                # Final outputs
└── docs/                   # Documentation and reports
```

---

## 🔗 Key Findings and References

* There is a positive association between the number of clean policies and green investment across countries. 
* This relationship varies by country context. The interaction analysis suggests that the policy–investment relationship is strongest in countries with higher income and stronger rule of law (Cluster 1), while the difference is weaker for low-income countries. 
* These findings imply that institutional quality and economic development may enhance the effectiveness of climate policies in attracting green investment. 
