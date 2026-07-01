# Quantitative Assessment of Climate Policy Effectiveness on Infrastructure Investment

## Analysis methodology
### Alignment between datasets
* Since the PPI dataset can only account for "green" energy projects vs other energy projects, focusing on resilience is a bit difficult. 
* We align the analysis on clean energy, by matching PPI data with policies related to clean energy such as renewables promotion or energy efficiency mandates. 
* Since policies take time to have an impact, we consider [2016, 2024] for the PPI data and [2014, 2022] for the policy data.

### Filtering of CPDB dataset
* Jurisdiction: National or country level
* Status: in force during the considered period
* Keywords:
   * From the text analysis, just looking at keywords like wind, solar, renewable gave a score of zero for about 21 countries.
   * We use the database's structured columns policy_type, sector. A clean energy policy is policy_type in {renewables, energy efficiency} or sector in {renewables, electricity}
   * Again, we could do more complicated stuff here if needed....

### Investment classification
cf Russell's work. 

### Metrics
We tested two metrics to represent a country's policy landscape:
* Green Policy Count : The total count of clean energy policies passed by a country.
* Green Policy Share: The proportion of clean energy policies out of a country's total national climate policies
Why this is useful: Count is biased towards larger countries with high bureaucratic resources. Share captures a country's specific policy focus.

### We try to see if there is a bias based on the amount of investment (some countries have very low investment)
We isolate the 20 top countries in terms of clean policy count, green investment, total investment.

### Step 7: Results and the "Policy-Investment Share Paradox"
Our final calculation yielded the following key Pearson correlations (\(r\)):

* **Policy Count vs. Absolute Investment (\(r \approx 0.81\) overall, \(0.69\) in top markets)**:
  * *Meaning*: Very strong positive correlation. Larger grid systems and larger economies pass more policies and attract more green dollars. This is a **scale effect**.
* **Green Policy Share vs. Green Investment Share (\(r \approx 0.02\) overall, but \(-0.44\) in top investment markets)**:
  * *Meaning*: In major markets, there is a **strong negative correlation**. 
    1. **Policy Breadth**: Major markets like China, India, and Brazil deploy comprehensive climate strategies that cover forestry, agriculture, industrial emissions, and carbon pricing. Because their total policy portfolio (\(N_c\)) is so large, their *share* of green policies (\(S_{p,c}\)) is mathematically low. Yet, their grids are clean-energy leaders and capture huge green investment shares.
    2. **Paper Policies**: Smaller countries often have highly focused, green-only policy portfolios (resulting in a high \(S_{p,c}\) of \(80\%-100\%\)), but due to financing constraints, grid integration problems, or political instability, they struggle to translate these policies into actual green projects (resulting in low or zero investment shares).
    3. **Conclusion**: Simply shifting the proportion of policy text towards green energy does not guarantee a higher green share of investments in developing economies. System scale, grid readiness, and investment environment are the dominant factors.


# LLM generated report for more details - An Empirical Replication and Extension of Policy Adoption vs. Green Infrastructure Investment

---

## 1. Introduction and Conceptual Framework

This report presents a rigorous empirical analysis investigating whether national climate policy adoption correlates with subsequent private infrastructure investments in clean energy across developing markets. We build upon the methodology of expanding policy-to-investment relationships (similar to Figure 2 in *Nature, 2023*) by implementing a structured policy identification pipeline, a formal temporal lag structure, and multidimensional investment metrics.

We evaluate the relationship under two main variables:
1. **Policy Metric (\(X\))**: The volume and focus of clean energy policy.
2. **Investment Metric (\(Y\))**: Absolute green infrastructure investment and its share of the total energy investment portfolio.

---

## 2. Mathematical Formulations and Definitions

### 2.1. Policy Dataset & Classification
Let \(D_P\) be the climate policy database containing policies \(p_k\). We restrict our policy set to national-level policies in force during the policy window \([t_{\text{start}}, t_{\text{end}}]\):

\[P_{\text{national}} = \{ p_k \mid \text{jurisdiction}(p_k) \in \{\text{"National"}, \text{"Country"}\} \land \text{status}(p_k) = \text{"In force"} \land \text{active}(p_k, t_{\text{start}}, t_{\text{end}}) \}\]

A policy \(p_k\) is classified as a **Clean Energy Policy** (\(C_k \in \{0, 1\}\)) based on its structured sectoral and policy type classifications:

\[C_k = \mathbb{I}\left( \text{Renewables} \in \text{policy\_type}(p_k) \lor \text{Energy efficiency} \in \text{policy\_type}(p_k) \lor \text{Renewables} \in \text{sector}(p_k) \lor \text{Electricity} \in \text{sector}(p_k) \right)\]

where \(\mathbb{I}(\cdot)\) is the indicator function.

For each country \(c\), we compute two metrics:
1. **Clean Energy Policy Count (\(P_c\))**:
   \[P_c = \sum_{p_k \in P_{\text{national}}, \text{country}(p_k)=c} C_k\]

2. **Green Policy Share (\(S_{p,c}\))**:
   \[S_{p,c} = \frac{P_c}{N_c} = \frac{\sum_{p_k \in P_{\text{national}}, \text{country}(p_k)=c} C_k}{\sum_{p_k \in P_{\text{national}}, \text{country}(p_k)=c} 1}\]
   where \(N_c\) is the total number of national, in-force climate policies for country \(c\).

---

### 2.2. Private Investment in Infrastructure (PPI)
Let \(D_I\) be the project investment database. Each project \(j\) for country \(c\) closed in year \(t\) has an investment value \(V_j\) (in Millions USD) and a technology classification.

We map each project technology to a binary category \(g_j\) (Green) or \(b_j\) (Brown):
- **Green (Narrow) (\(G_{\text{narrow}}\))**: Solar, Wind, Geothermal, Biomass, Small Hydro (\(<50\text{MW}\)).
- **Brown (\(B\))**: Coal, Natural Gas, Diesel, Steam.
- **Green (Broad Extra) (\(G_{\text{broad}}\))**: Large Hydro (\(>50\text{MW}\)), Waste-to-Energy.

For a project \(j\):
\[\text{is\_green}(j) = \begin{cases} 
1 & \text{if } \text{technology}(j) \in G_{\text{narrow}} \\
0 & \text{if } \text{technology}(j) \in B \\
\text{NaN} & \text{otherwise} 
\end{cases}\]

\[\text{is\_green\_broad}(j) = \begin{cases} 
1 & \text{if } \text{technology}(j) \in G_{\text{narrow}} \cup G_{\text{broad}} \\
0 & \text{if } \text{technology}(j) \in B \\
\text{NaN} & \text{otherwise} 
\end{cases}\]

Let \(T_c\) be the set of projects closed in country \(c\) during the investment window. The aggregate investment metrics are:
1. **Absolute Green Investment (\(I_{g,c}\))**:
   \[I_{g,c} = \sum_{j \in T_c} V_j \cdot \mathbb{I}(\text{is\_green}(j) == 1)\]

2. **Green Investment Share (\(S_{i,c}\))**:
   \[S_{i,c} = \frac{\sum_{j \in T_c} V_j \cdot \mathbb{I}(\text{is\_green}(j) == 1)}{\sum_{j \in T_c} V_j \cdot \mathbb{I}(\text{is\_green}(j) \in \{0, 1\})}\]

---

### 2.3. Temporal Lag Structure
To model the time required for policies to influence capital deployment, we implement a **2-year lag (\(\Delta t = 2\))**:
- **Policy Window**: Cumulative policies active during \([2014, 2022]\) (cumulative up to \(t - 2\)).
- **Investment Window**: Total investments closed during \([2016, 2024]\).

---

### 2.4. Statistical Metric: Pearson Correlation Coefficient (\(r\))
For two variables \(X\) and \(Y\) across a sample size \(n\) of countries:

\[r = \frac{\sum_{i=1}^n (X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum_{i=1}^n (X_i - \bar{X})^2 \sum_{i=1}^n (Y_i - \bar{Y})^2}}\]

---

## 3. Detailed Results and Correlation Analysis

The correlations are computed for all matched developing countries (\(N = 95\)) and then restricted to the **Top 20 countries** under three different definitions of "Top" to isolate market size effects.

### Pearson Correlation Matrix (\(r\))

| Subpopulation Filter | \(P_c\) vs. \(I_{g,c}\) <br> *(Policy Count vs. Absolute Green Investment)* | \(P_c\) vs. \(S_{i,c}\) <br> *(Policy Count vs. Green Share)* | \(S_{p,c}\) vs. \(S_{i,c}\) <br> *(Green Policy Share vs. Green Investment Share)* |
| :--- | :---: | :---: | :---: |
| **All Matched Countries (N=95)** | **0.805** | -0.045 | 0.020 |
| **Top 20 by Clean Policy Count** | **0.674** | -0.044 | **-0.371** |
| **Top 20 by Green Investment** | **0.675** | -0.067 | **-0.338** |
| **Top 20 by Total Investment** | **0.687** | 0.151 | **-0.443** |

---

## 4. Analytical Interpretations

### 4.1. The Scale Effect (\(P_c\) vs. \(I_{g,c}\))
The extremely strong positive correlation (\(r = 0.805\) overall) indicates that absolute clean policy volume strongly tracks absolute green investment. This is heavily driven by **country-scale factors**: larger developing economies (e.g., China, India, Brazil, Vietnam) naturally possess both larger bureaucratic capacity to pass policies and larger power grids requiring massive absolute capital deployment.

### 4.2. The Policy-Investment Share Paradox (\(S_{p,c}\) vs. \(S_{i,c}\))
The most critical finding is the negative correlation (\(r = -0.443\) in top investment markets) between the **proportion of green policies** (\(S_{p,c}\)) and the **proportion of green investments** (\(S_{i,c}\)). 

#### Why is this negative?
1. **Policy Focus vs. Policy Breadth**: Major markets (like China or Brazil) deploy comprehensive climate strategies that target forestry, agriculture, industrial emissions, and coal transition. This broad coverage mathematically *lowers* their Green Policy Share (\(S_{p,c}\)) because total climate policies (\(N_c\)) is large. Yet, due to their grid scale, they attract huge green shares (\(S_{i,c}\)) in energy investments.
2. **Green-Only Paper Policies**: Conversely, some smaller countries have highly focused climate portfolios that target only renewables (yielding a high \(S_{p,c}\) of \(80\%-100\%\)), but suffer from financing constraints, grid capacity limitations, or political instability that prevent them from translating these policies into actual green projects, leading to low or zero \(S_{i,c}\).

---

## 5. Conclusion
For developing nations, increasing the *fraction* of clean energy policies relative to total climate policies is not associated with a corresponding increase in the share of green infrastructure investments. Rather, absolute policy capacity and broader economic/grid scales dominate the deployment of green capital.
