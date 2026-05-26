# Project Proposal: Quantifying the Effect of Carbon Pricing on Private Capital Allocation for Resilient Infrastructure
**Date:** May 26, 2026 (Updated from May 12 Meeting)  
**Project Group Task:** Updated Draft

---

## 1. Title
**Quantifying the Effect of Carbon Pricing on Private Capital Allocation for Resilient Infrastructure**

*Note from Meeting:* We evaluated alternative policy instruments (such as climate risk disclosure mandates, NDCs, etc.) and determined that focusing on **Carbon Pricing mechanisms** (e.g., carbon taxes and Emissions Trading Systems) provides a more established, quantifiable, and direct price signal for analyzing private capital flows into resilient infrastructure projects.

---

## 2. Research Questions

### Domestic Policy Impact
* Does the implementation of domestic carbon pricing mechanisms (carbon taxes or Emissions Trading Systems - ETS) by a host country correlate with a statistically significant increase in the proportion of private investment directed toward resilient infrastructure projects?  
*Data note:* We will extract policy implementation years, scope, and effective price rates per metric ton of $\text{CO}_2$ equivalent.

### Transnational / Cross-Border Spillover Effects
* To what extent do high carbon prices or strict compliance mechanisms in an institutional investor's home country (e.g., the EU's Carbon Border Adjustment Mechanism [CBAM] or high domestic ETS price signals) influence their "green-to-brown" infrastructure investment ratio within emerging market project pipelines?

### Moderating Variables
* How do global and local macroeconomic uncertainties, as measured by the World Uncertainty Index (WUI), affect the transmission mechanism between carbon pricing policies and actual private capital mobilization?

---

## 3. Datasets

* **World Bank Private Participation in Infrastructure (PPI) Database:** Used for project-level data, including total private investment commitments, sectoral classifications (Energy, Water, Transport), technology categories (Solar, Wind, Hydro vs. Coal, Gas), and the country of origin of private sponsors/investors.
* **World Bank Carbon Pricing Dashboard / Climate Policy Database:** Used to track specific adoption years, sector coverage, implementation statuses, and historical nominal/effective price paths of carbon taxes and Emissions Trading Systems (ETS) across multiple jurisdictions.
* **IMF Climate Change Indicators Dashboard:** Provides necessary country-level macro controls, including country-level greenhouse gas emissions intensity, carbon footprint profiles, and baseline physical climate risk vulnerabilities.
* **World Uncertainty Index (WUI):** Utilized to extract high-frequency country-level data on economic and policy uncertainty, acting as a critical control variable in our econometric models to capture market volatility.
* **IEA/IRENA Policies and Measures Database:** Used as a complementary dataset to cross-verify specific clean energy investment incentives and tax exemptions aligned with carbon pricing frameworks.

---

## 4. Methods

### Data Preparation and Integration
1.  **Entity Resolution:** Standardize country names, regional classifications, and temporal variables across disparate data platforms (World Bank, IMF, WUI).
2.  **Asset Classification:** Categorize infrastructure investments from the PPI database into **"Resilient / Green"** (e.g., utility-scale renewable energy, climate-resilient water treatments, electrified public transit) and **"Non-Resilient / Conventional"** (e.g., unabated fossil-fuel power plants, traditional asphalt road networks) based on sector, sub-sector, and technology identifiers.

### Feature Engineering
* **Green Investment Ratio ($Ratio_{c,t}$):** Calculate the primary dependent variable per country $c$ in year $t$:
    $$\text{Ratio}_{c,t} = \frac{\text{Resilient Investment}_{c,t}}{\text{Total Private Infrastructure Investment}_{c,t}}$$
* **Policy Treatment Variable:** * *Approach A:* Construct a binary "Policy Treatment" indicator variable based on the active enforcement date of a carbon pricing mechanism.
    * *Approach B:* Construct a continuous metric capturing the real or effective carbon price ($/t\text{CO}_2e$) to measure policy intensity.

### Econometric Analysis Specifications
* **Difference-in-Differences (DiD) Design:** Estimate the causal impact of carbon pricing adoption by evaluating shifting investment trajectories in "treated" economies (countries implementing carbon pricing) against a statistically matched control group of non-adopting jurisdictions.
* **Panel Fixed-Effects Regression:** Build an interactive panel framework utilizing Python's `linearmodels` or `statsmodels` libraries. This model will explicitly control for time-invariant country-specific factors (e.g., institutional framework quality) and global annual macro shocks.
* **Lagged Variable Analysis:** Incorporate 1-year, 2-year, and 3-year temporal lags on the policy variables to naturally account for the multi-year project finance lifecycle and structural duration between carbon policy execution and final project financial closure.

---

## 5. Outputs

* **Technical Repository:** A fully reproducible, documented Python codebase (hosted in Jupyter Notebooks) detailing the processing pipeline: data cleaning, multi-source merging, variable transformations, and econometric output generation.
* **Econometric Summary & Tables:** Formatted regression output matrices displaying estimated coefficients, robust standard errors, $R^2$ values, and statistical significance levels evaluating the policy's impact on green capital mobilization.
* **Data Visualizations:**
    * *Event-Study Plots:* Time-series visualizations showing parallel trend validation and capital deployment trajectories before and after carbon pricing "Year Zero."
    * *Geographic Heatmaps:* Spatial visualizations tracking the evolution of resilient infrastructure project financing volumes relative to localized carbon pricing updates.
* **Policy Analysis Report:** A formal synthesis detailing the empirical efficacy of carbon pricing models in accelerating private asset re-allocation toward climate-aligned projects, including concrete recommendations for policy-makers.

---

## 6. Expected Results

* **Positive Policy Correlation:** We expect a statistically significant, positive relationship between the presence of an active carbon price and the subsequent share of private capital allocated to resilient infrastructure, as carbon pricing increases the relative operational cost of high-emission alternatives.
* **Cross-Border Spillover Effects:** The analysis will likely show that multinational capital or institutional investors subject to strict home-region carbon policies (or import border adjustments like CBAM) favor resilient asset classes when expanding pipelines into emerging markets.
* **Uncertainty Sensitivity (Moderating Effect):** We expect a negative interaction coefficient between high macroeconomic uncertainty (WUI) and carbon pricing efficacy, validating the hypothesis that regulatory price signals are less effective at motivating long-term infrastructure investment during volatile macroeconomic cycles.
* **Implementation and Adjustment Lags:** The data is anticipated to show an empirical lag of approximately 18 to 24 months from the initial enactment/tightening of carbon pricing laws to observable adjustments in actual project financial closings due to long procurement timelines.

---

## 7. Literature Review (Target Additions)

* Biagini, B., & Miller, A. (2013). Engaging the private sector in adaptation to climate change in developing countries: importance, status, and challenges. *Climate and Development*, 5(3), 242–252. https://doi.org/10.1080/17565529.2013.821053
* Best, R., Burke, P. J., & Jotzo, F. (2020). Carbon pricing efficacious in reducing carbon emissions. *Nature Climate Change*, 10(12), 1061-1064.
* Sen, S., & Vollebergh, H. R. (2018). The impact of carbon pricing on eco-innovation: Evidence from EU countries. *Energy Economics*, 76, 128-136.