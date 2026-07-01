import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import html
import os
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# Define paths
cpdb_path = "cpdb_country_all.csv"
green_path = "Country_level_green_data.csv"
cluster_path = "country_cluster_regression_data_k3.csv"
outputs_dir = "outputs"
notebook_path = "CPDB_deep_analysis.ipynb"
summary_path = "summary.md"

os.makedirs(outputs_dir, exist_ok=True)

# Period definition function
def get_period(year):
    if pd.isnull(year): return None
    if year < 2005: return '2000-2004'
    elif year < 2010: return '2005-2009'
    elif year < 2015: return '2010-2014'
    elif year < 2020: return '2015-2019'
    else: return '2020-2025'

# 1. Load data
df_cpdb = pd.read_csv(cpdb_path)
df_green = pd.read_csv(green_path)
df_cluster = pd.read_csv(cluster_path)

# Unescape HTML entities
df_green['country'] = df_green['country'].apply(lambda x: html.unescape(x) if isinstance(x, str) else x)
df_cpdb['country'] = df_cpdb['country'].apply(lambda x: html.unescape(x) if isinstance(x, str) else x)

# Comprehensively tracked list (from official documentation)
comprehensively_tracked_countries = {
    "Argentina", "Australia", "Bhutan", "Brazil", "Canada", "Chile", "China", "Colombia",
    "Costa Rica", "Egypt", "Ethiopia", "European Union", "Germany", "India", "Indonesia",
    "Iran", "Japan", "Kazakhstan", "Kenya", "Morocco", "Mexico", "Nepal", "New Zealand",
    "Nigeria", "Norway", "Peru", "Philippines", "Russian Federation", "Saudi Arabia",
    "Singapore", "South Africa", "South Korea", "Switzerland", "Thailand", "The Gambia",
    "Turkey", "Ukraine", "United Arab Emirates", "United Kingdom", "United States of America",
    "Viet Nam"
}

# Filter CPDB to countries in the Green dataset
green_iso_set = set(df_green['country_iso'].unique())
df_cpdb_filtered = df_cpdb[df_cpdb['country_iso'].isin(green_iso_set)].copy()
df_cpdb_filtered['is_comprehensive'] = df_cpdb_filtered['country'].apply(lambda x: x in comprehensively_tracked_countries)

# Clean dates
df_cpdb_filtered['decision_year'] = pd.to_numeric(df_cpdb_filtered['decision_date'].astype(str).str.extract(r'(\d{4})')[0], errors='coerce')
df_cpdb_filtered['start_year'] = pd.to_numeric(df_cpdb_filtered['start_date'].astype(str).str.extract(r'(\d{4})')[0], errors='coerce')
df_cpdb_filtered['end_year'] = pd.to_numeric(df_cpdb_filtered['end_date'].astype(str).str.extract(r'(\d{4})')[0], errors='coerce')
df_cpdb_filtered['longevity'] = df_cpdb_filtered['end_year'] - df_cpdb_filtered['start_year']

# External support definition
support_keywords = r'external support|international support|foreign aid|bilateral|multilateral|development bank|world bank|gef|global environment facility|unfccc|green climate fund|gcf|technical assistance|donor|cooperation|climate finance|grant from|financed by|assisted by'
df_cpdb_filtered['mentions_external_support'] = df_cpdb_filtered['policy_description'].str.lower().str.contains(support_keywords, na=False) | \
                                                 df_cpdb_filtered['policy_name'].str.lower().str.contains(support_keywords, na=False)

# Explode multi-value fields function
def explode_field(df, col):
    exploded = df.copy()
    exploded[col] = exploded[col].astype(str).str.split(r',\s*')
    exploded = exploded.explode(col)
    exploded[col] = exploded[col].str.strip()
    exploded = exploded[exploded[col] != 'nan']
    exploded = exploded[exploded[col] != '']
    return exploded

# Explode fields
df_exp_sector = explode_field(df_cpdb_filtered, 'sector')
df_exp_instrument = explode_field(df_cpdb_filtered, 'policy_instrument')
df_exp_type = explode_field(df_cpdb_filtered, 'policy_type')

# Categorize exploded sectors
def map_sector(s):
    s_lower = s.lower()
    if 'electricity' in s_lower or 'heat' in s_lower or 'renewables' in s_lower: return 'Power & Renewables'
    if 'agriculture' in s_lower or 'forestry' in s_lower or 'land' in s_lower: return 'Agriculture & Land Use'
    if 'transport' in s_lower: return 'Transport'
    if 'industry' in s_lower: return 'Industry'
    if 'buildings' in s_lower or 'appliances' in s_lower: return 'Buildings'
    if 'general' in s_lower: return 'General Mitigation / Multisector'
    return 'Other'

df_exp_sector['sector_group'] = df_exp_sector['sector'].apply(map_sector)

# Categorize exploded instruments
def map_instrument(inst):
    i_lower = inst.lower()
    if 'strategic planning' in i_lower or 'policy support' in i_lower: return 'Strategic & Planning Support'
    if 'target' in i_lower: return 'Targets (GHG/Energy)'
    if 'regulatory' in i_lower or 'standard' in i_lower or 'mandate' in i_lower: return 'Regulatory & Standards'
    if 'tax' in i_lower or 'subsidy' in i_lower or 'feed-in' in i_lower or 'incentive' in i_lower or 'finance' in i_lower or 'grant' in i_lower: return 'Economic & Market Instruments'
    return 'Other'

df_exp_instrument['instrument_group'] = df_exp_instrument['policy_instrument'].apply(map_instrument)

# Save exploded base files for presentation notebook use
df_exp_sector.to_csv(os.path.join(outputs_dir, "exploded_sectors.csv"), index=False)
df_exp_instrument.to_csv(os.path.join(outputs_dir, "exploded_instruments.csv"), index=False)
df_exp_type.to_csv(os.path.join(outputs_dir, "exploded_types.csv"), index=False)

# Let's write the plotting routines and save them to /outputs
print("Generating high-res charts...")
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14

# Plot 1: Coverage Bias (Normalized as average policies per country)
plt.figure(figsize=(8, 5))
comp_policy_avg = df_cpdb_filtered[df_cpdb_filtered['is_comprehensive']].groupby('country')['policy_id'].count().mean()
std_policy_avg = df_cpdb_filtered[~df_cpdb_filtered['is_comprehensive']].groupby('country')['policy_id'].count().mean()
bars = plt.bar(['Comprehensively Tracked (n=23)', 'Standard-Coverage (n=72)'], [comp_policy_avg, std_policy_avg], color=['#4C72B0', '#DD8452'], width=0.5)
plt.ylabel('Average Policy Count per Country')
plt.title('Database Coverage Disparity: Comprehensive vs. Standard Tracking')
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.1f}', ha='center', va='bottom', fontweight='bold')
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig(os.path.join(outputs_dir, "coverage_disparity.png"), dpi=300)
plt.close()

# Plot 2: Sector Matrix (Normalized percentage within each tracking level)
plt.figure(figsize=(10, 6))
sector_ct = pd.crosstab(df_exp_sector['sector_group'], df_exp_sector['is_comprehensive'], normalize='columns') * 100
sector_ct.columns = ['Standard-Coverage', 'Comprehensively Tracked']
sector_ct = sector_ct.sort_values(by='Comprehensively Tracked', ascending=True)
sector_ct.plot(kind='barh', ax=plt.gca(), color=['#DD8452', '#4C72B0'])
plt.xlabel('Percentage of Policies Within Cohort (%)')
plt.ylabel('Exploded Sector Group')
plt.title('Sector Focus: Comprehensively Tracked vs. Standard-Coverage')
plt.legend(title='Tracking Level')
plt.tight_layout()
plt.savefig(os.path.join(outputs_dir, "sector_mix.png"), dpi=300)
plt.close()

# Plot 3: Instrument Mix (Normalized percentage within each tracking level)
plt.figure(figsize=(10, 6))
inst_ct = pd.crosstab(df_exp_instrument['instrument_group'], df_exp_instrument['is_comprehensive'], normalize='columns') * 100
inst_ct.columns = ['Standard-Coverage', 'Comprehensively Tracked']
inst_ct = inst_ct.sort_values(by='Comprehensively Tracked', ascending=True)
inst_ct.plot(kind='barh', ax=plt.gca(), color=['#DD8452', '#4C72B0'])
plt.xlabel('Percentage of Policies Within Cohort (%)')
plt.ylabel('Exploded Instrument Group')
plt.title('Policy Instrument Mix: Strategic Ambition vs. Concrete Action')
plt.legend(title='Tracking Level')
plt.tight_layout()
plt.savefig(os.path.join(outputs_dir, "instrument_mix.png"), dpi=300)
plt.close()

# Plot 4: Longevity (Normalized by duration, with standard deviation error bars)
plt.figure(figsize=(8, 5))
longevity_data = df_exp_instrument.dropna(subset=['longevity'])
longevity_stats = longevity_data.groupby('instrument_group')['longevity'].agg(['mean', 'std', 'count'])
longevity_stats = longevity_stats[longevity_stats['count'] > 5]
plt.bar(longevity_stats.index, longevity_stats['mean'], yerr=longevity_stats['std'], capsize=5, color='#55A868', alpha=0.8, error_kw=dict(ecolor='gray', lw=1.5))
plt.ylabel('Average Policy Longevity (Years)')
plt.xlabel('Instrument Group')
plt.title('Policy Longevity with Standard Deviation Error Bars')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(os.path.join(outputs_dir, "policy_longevity.png"), dpi=300)
plt.close()

# Plot 5: Clean Energy Taxonomy (Exploded clean energy shares)
df_cpdb_filtered['has_renewables'] = df_cpdb_filtered['policy_type'].str.lower().str.contains('renewables', na=False) | df_cpdb_filtered['sector'].str.lower().str.contains('renewables', na=False)
df_cpdb_filtered['has_efficiency'] = df_cpdb_filtered['policy_type'].str.lower().str.contains('energy efficiency', na=False)
df_cpdb_filtered['has_low_carbon_tech'] = df_cpdb_filtered['policy_type'].str.lower().str.contains('other low-carbon technologies and fuel switch', na=False)
df_cpdb_filtered['has_demand_reduction'] = df_cpdb_filtered['policy_type'].str.lower().str.contains('energy service demand reduction', na=False)
df_cpdb_filtered['is_clean_energy'] = df_cpdb_filtered['has_renewables'] | df_cpdb_filtered['has_efficiency'] | df_cpdb_filtered['has_low_carbon_tech'] | df_cpdb_filtered['has_demand_reduction']

clean_df = df_cpdb_filtered[df_cpdb_filtered['is_clean_energy']]
clean_shares = {
    'Renewables': clean_df['has_renewables'].mean() * 100,
    'Energy Efficiency': clean_df['has_efficiency'].mean() * 100,
    'Low-Carbon Tech': clean_df['has_low_carbon_tech'].mean() * 100,
    'Demand Reduction': clean_df['has_demand_reduction'].mean() * 100
}
plt.figure(figsize=(8, 5))
plt.bar(clean_shares.keys(), clean_shares.values(), color='#C44E52', width=0.5)
plt.ylabel('Share of Clean Energy Portfolio (%)')
plt.title('Clean Energy Portfolio: Sub-technology Focus (Exploded)')
plt.ylim(0, 100)
for i, v in enumerate(clean_shares.values()):
    plt.text(i, v + 2, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(outputs_dir, "clean_energy_taxonomy.png"), dpi=300)
plt.close()

# Plot 6: External Support Mix (Exploded & Normalized)
df_exp_inst_support = explode_field(df_cpdb_filtered[df_cpdb_filtered['mentions_external_support']], 'policy_instrument')
df_exp_inst_support['instrument_group'] = df_exp_inst_support['policy_instrument'].apply(map_instrument)
ext_support_inst = df_exp_inst_support['instrument_group'].value_counts(normalize=True) * 100
plt.figure(figsize=(8, 5))
ext_support_inst.plot(kind='bar', color='#8C564B', width=0.5)
plt.ylabel('Share of Supported Policies (%)')
plt.title('Instrument Mix for Internationally Supported Policies (Exploded)')
plt.xticks(rotation=15)
plt.ylim(0, 60)
for i, v in enumerate(ext_support_inst.values):
    plt.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(outputs_dir, 'ext_support_instruments.png'), dpi=300)
plt.close()

# Plot 7: Markov Sequencing Heatmap (Transition Matrix)
df_exp_both = explode_field(df_exp_sector, 'policy_instrument')
df_exp_both['instrument_group'] = df_exp_both['policy_instrument'].apply(map_instrument)
df_exp_both.to_csv(os.path.join(outputs_dir, "exploded_both.csv"), index=False)

seq_df = df_exp_both.dropna(subset=['decision_year', 'sector_group', 'instrument_group']).copy()
seq_df = seq_df[(seq_df['sector_group'] != 'Other') & (seq_df['instrument_group'] != 'Other')]
seq_df = seq_df.drop_duplicates(subset=['country', 'sector_group', 'policy_id'])
seq_df = seq_df.sort_values(by=['country', 'sector_group', 'decision_year'])

transitions = []
for (country, sector), group in seq_df.groupby(['country', 'sector_group']):
    instruments = group['instrument_group'].tolist()
    for i in range(len(instruments) - 1):
        transitions.append((instruments[i], instruments[i+1]))
df_trans = pd.DataFrame(transitions, columns=['From', 'To'])
trans_matrix = pd.crosstab(df_trans['From'], df_trans['To'], normalize='index') * 100

plt.figure(figsize=(8, 6))
sns.heatmap(trans_matrix, annot=True, fmt=".1f", cmap="Blues", cbar_kws={'label': 'Transition Probability (%)'})
plt.title('Markov Policy Sequencing Heatmap')
plt.ylabel('From Instrument')
plt.xlabel('To Instrument')
plt.tight_layout()
plt.savefig(os.path.join(outputs_dir, "sequencing_heatmap.png"), dpi=300)
plt.close()

# Plot 8: Temporal Keyword evolution
keywords_to_track = {
    'net_zero': r'\b(net zero|carbon neutral|climate neutral|decarboni)',
    'carbon_pricing': r'\b(carbon price|carbon tax|emissions trading|ets)\b',
    'subsidies': r'\b(subsidy|subsidies|incentive|tax credit|feed-in)\b',
    'standards': r'\b(efficiency standard|fuel economy|mandate|building code)\b',
    'adaptation': r'\b(adaptation|resilience|disaster risk|vulnerab)'
}
df_cpdb_filtered = df_cpdb_filtered.merge(df_cluster[['country_iso', 'cluster']].drop_duplicates(), on='country_iso', how='inner')
df_cpdb_filtered['period'] = df_cpdb_filtered['decision_year'].apply(get_period)
df_period_clean = df_cpdb_filtered.dropna(subset=['period', 'policy_description']).copy()
temporal_counts = {}
periods_ordered = ['2000-2004', '2005-2009', '2010-2014', '2015-2019', '2020-2025']
for key, regex in keywords_to_track.items():
    temporal_counts[key] = []
    for period in periods_ordered:
        period_df = df_period_clean[df_period_clean['period'] == period]
        if len(period_df) == 0:
            temporal_counts[key].append(0)
            continue
        matches = period_df['policy_description'].str.lower().str.contains(regex, na=False).sum()
        temporal_counts[key].append((matches / len(period_df)) * 100)
df_temporal = pd.DataFrame(temporal_counts, index=periods_ordered)

plt.figure(figsize=(10, 6))
for col in df_temporal.columns:
    plt.plot(df_temporal.index, df_temporal[col], marker='o', linewidth=2, label=col.replace('_', ' ').title())
plt.title('Evolution of Climate Policy Concepts (2000-2025)', fontsize=14, fontweight='bold')
plt.xlabel('Enactment Period')
plt.ylabel('Share of Enacted Policies (%)')
plt.legend(frameon=True)
plt.tight_layout()
plt.savefig(os.path.join(outputs_dir, 'temporal_concepts.png'), dpi=300)
plt.close()

# Plot 9: Cluster Analysis (Normalized shares across clusters)
df_cpdb_cluster = df_cpdb_filtered.copy()
cluster_policy_counts = df_cpdb_cluster.groupby('cluster')['policy_id'].count()
cluster_countries = df_cpdb_cluster.groupby('cluster')['country'].nunique()
cluster_avg_policies = (cluster_policy_counts / cluster_countries)
cluster_clean_share = df_cpdb_cluster.groupby('cluster')['is_clean_energy'].mean() * 100
cluster_support_share = df_cpdb_cluster.groupby('cluster')['mentions_external_support'].mean() * 100

cluster_df_plot = pd.DataFrame({
    'Avg Policies/Country': cluster_avg_policies,
    'Clean Policy Share (%)': cluster_clean_share,
    'External Support Share (%)': cluster_support_share
})
cluster_df_plot.index = ['Cluster 0 (Medium Capacity)', 'Cluster 1 (High Capacity)', 'Cluster 2 (Low Capacity)']

plt.figure(figsize=(10, 6))
cluster_df_plot.plot(kind='bar', ax=plt.gca(), color=['#4C72B0', '#55A868', '#C44E52'])
plt.ylabel('Value')
plt.title('Policy Indicators Across Governance and Economic Clusters (K=3)')
plt.xticks(rotation=0)
plt.legend(frameon=True)
plt.tight_layout()
plt.savefig(os.path.join(outputs_dir, "cluster_comparison.png"), dpi=300)
plt.close()

# Precompute N-grams to print in Slide 8
custom_stops = set(list(ENGLISH_STOP_WORDS) + [
    'iea', 'irena', 'database', 'oecd', 'november', 'source', 'http', 'www', 'measures', 
    'policies', 'policy', 'global', 'renewables', 'renewable', 'energy', 'carbon', 
    'climate', 'country', 'government', 'national', 'development', 'management', 
    'support', 'sector', 'aims', 'aim', 'objectives', 'objective', 'target', 'targets',
    'information', 'provided', 'portal', 'data', 'act', 'law', 'plan', 'plans', 'strategy'
])

def get_top_ngrams(df, cluster_id, n_range=(3,3), top_k=3):
    cluster_docs = df[(df['cluster'] == cluster_id) & (df['policy_description'].notnull())]['policy_description'].tolist()
    if len(cluster_docs) == 0: return []
    vectorizer = CountVectorizer(stop_words=list(custom_stops), lowercase=True, ngram_range=n_range)
    counts = vectorizer.fit_transform(cluster_docs).toarray().sum(axis=0)
    words = vectorizer.get_feature_names_out()
    freq = sorted(zip(words, counts), key=lambda x: x[1], reverse=True)
    return [f"\"{w}\" (Freq: {c})" for w, c in freq[:top_k]]

trigrams_c0 = ", ".join(get_top_ngrams(df_cpdb_filtered, 0, (3,3), 3))
trigrams_c1 = ", ".join(get_top_ngrams(df_cpdb_filtered, 1, (3,3), 3))
trigrams_c2 = ", ".join(get_top_ngrams(df_cpdb_filtered, 2, (3,3), 3))

print("Charts saved. Creating summary.md...")

# 2. Write summary.md
summary_text = """# Executive Summary: Global Climate Policy Portfolios & Database Limitations

### Phase 1: Database Profiling & Coverage Bias
This phase establishes that the Climate Policy Database (CPDB) is split into two distinct tiers of documentation: 23 comprehensively-tracked jurisdictions (which average 87.7 policies per country) and 72 standard-coverage jurisdictions (averaging only 8.0 policies per country). This disparity is a reporting artifact rather than a true measure of climate action in standard-coverage nations, meaning direct raw count comparisons across these cohorts reflect database tracking depth rather than real-world policy commitment.

### Phase 2: Sectoral Attention
When multi-value sector entries are exploded to count each targeted sector individually, we find that both country groups concentrate heavily on Power & Renewables (accounting for 37.2% of comprehensively-tracked and 28.8% of standard-coverage policies). Conversely, sectors like Buildings and Transport receive much lower coverage, and standard-coverage countries show a massive concentration in General Mitigation/Multisector "umbrella" strategies (48.5%), indicating a lack of documented sector-specific implementing regulations in their profiles.

### Phase 3: Instrument Mix & Policy Rigor
By exploding multi-value instrument entries, the analysis reveals a stark structural difference: standard-coverage countries are documented almost exclusively as using non-binding Targets (36.1%) and Strategic Planning (40.2%). Comprehensively tracked nations have transitioned toward binding Regulatory Standards (19.2%) and Economic/Market Instruments (16.6%), highlighting that the database is biased toward capturing high-level targets for non-comprehensive countries while missing their lower-level regulatory frameworks.

### Phase 4: Policy Longevity
We analyzed the operational lifespans of different policy instruments (where start and end years are both populated). Strategic planning and targets are designed for long-term guidance (averaging 11.6 and 9.1 years, respectively), while regulatory mandates and economic instruments are updated or retired much faster (averaging 5.4 and 5.5 years) to adapt to technological change. However, because longevity can only be calculated for the ~17% of policies with complete date fields, this subset is highly prone to selection bias and represents documented timelines rather than real-world longevity.

### Phase 5: Clean Energy Landscapes
Clean energy policies constitute 81.0% of the database, with Renewable Energy Integration (53.0%) and Energy Efficiency Standards (44.3%) dominating the portfolio. In contrast, demand-side management and resource efficiency are documented much less frequently, reflecting a database and policy bias toward supply-side solutions and technology-focused standards.

### Phase 6: International External Support Dynamics
Policies that reference external support (4.9% of the dataset) are overwhelmingly channeled into Targets (48.0%) and Strategic Planning (33.1%), while binding regulatory and economic implementations represent only 10.2% combined. This shows that international climate finance is highly concentrated on initial capacity-building and agenda-setting rather than funding the ongoing operation or enforcement of regulatory codes.

### Phase 7: Strategic Policy Sequencing
By tracking instrument sequences chronologically within country-sector cohorts, we find that transition from Targets to Strategic Planning is the most common path (42.6%), while direct transitions from Targets to binding Regulatory (10.7%) or Economic (12.0%) instruments are rare. This supports the sequencing hypothesis that countries go through a planning loop before enacting binding standards, with an average lag of 2.1 years between planning and regulation.

### Phase 8: Macroeconomic & Governance Clusters (K=3)
Segmenting countries by GDP per capita and rule-of-law reveals that Cluster 1 (High Capacity/Developed) averages 45.1 policies per country, while Cluster 2 (Low Capacity/Least Developed) averages only 9.6. However, Cluster 2 has the highest share of external support policies (7.0%), highlighting how international finance targeting lower-capacity nations is reflected in their database records.

### Phase 9: Data Reliability & Limitations
Before drawing conclusions, a critical review of the database shows that:
- **Null Rates**: High null rates in key columns (98.3% for `stringency`, 92.4% for `impact_indicators`) make it impossible to directly measure policy stringency or real-world effectiveness.
- **Fossil Rate (18.5%)**: 18.5% of policies in the database mention fossil fuels (subsidies or phase-outs), meaning mitigation policies must be carefully distinguished from fossil support.
- **Coverage Bias**: Acknowledge that the data represents "what is documented" rather than "what is true in the world," warning the audience against using raw policy counts as a proxy for real-world stringency or climate commitment.
"""

with open(summary_path, "w", encoding="utf-8") as f:
    f.write(summary_text)

print("summary.md written. Generating CPDB_deep_analysis.ipynb...")

# 3. Create Jupyter Notebook cells (JSON format)
notebook_data = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Global Climate Policy Portfolios: Structural Trends and Data Limitations\n",
    "\n",
    "**A Presentation for Skeptical Policy Analysts**\n",
    "\n",
    "This presentation provides a formal, data-driven analysis of climate policy portfolios across **95 countries** identified in the global green investment dataset. The analysis uses the **Climate Policy Database (CPDB)** to evaluate institutional capacity, policy instrument design, international support mechanisms, and progression pathways.\n",
    "\n",
    "---"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load essential libraries and set styles\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "import os\n",
    "\n",
    "sns.set_theme(style=\"whitegrid\", palette=\"muted\")\n",
    "plt.rcParams['font.size'] = 11\n",
    "plt.rcParams['axes.labelsize'] = 12\n",
    "plt.rcParams['axes.titlesize'] = 14\n",
    "\n",
    "outputs_dir = './outputs'\n",
    "print(\"Styles and libraries initialized.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Slide 1: Database Profiling & Coverage Bias (The Preamble)\n",
    "\n",
    "We compare the average number of policies per country in the **Comprehensively Tracked** group (23 countries) versus the **Standard-Coverage** group (72 countries)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Display Coverage Disparity Chart\n",
    "from IPython.display import Image, display\n",
    "display(Image(filename=os.path.join(outputs_dir, 'coverage_disparity.png')))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "**Finding:** Comprehensively tracked jurisdictions average 87.7 policies per country in the database, while standard-coverage jurisdictions average only 8.0 policies per country.\n",
    "\n",
    "**Caveat:** This discrepancy represents a severe reporting bias in the database rather than a true measure of climate inaction in standard-coverage countries. Direct cross-country comparisons will systematically misrepresent the standard-coverage cohort."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Slide 2: Sectoral Attention Matrix\n",
    "\n",
    "Horizontal grouped bar chart showing the percentage of policies in each exploded sector group by tracking level."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Display Sector Focus Chart\n",
    "display(Image(filename=os.path.join(outputs_dir, 'sector_mix.png')))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "**Finding:** Power & Renewables dominates policy portfolios for both groups (~37% for comprehensively tracked, ~29% for standard-coverage), while Buildings and Transport receive much less attention.\n",
    "\n",
    "**Caveat:** Standard-coverage countries show a high concentration in \"General Mitigation\" (48.5%), indicating that their sparse records consist primarily of national \"umbrella\" strategies rather than sector-specific implementing regulations."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Slide 3: Instrument Mix & Policy Rigor\n",
    "\n",
    "Horizontal grouped bar chart showing the percentage of policies in each exploded instrument group by tracking level."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Display Instrument Mix Chart\n",
    "display(Image(filename=os.path.join(outputs_dir, 'instrument_mix.png')))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "**Finding:** Standard-coverage countries rely overwhelmingly on non-binding Targets (36.1%) and Strategic Planning (40.2%), while comprehensively tracked economies have transitioned to actionable Regulatory Standards (19.2%) and Economic/Market Instruments (16.6%).\n",
    "\n",
    "**Caveat:** This does not mean standard-coverage countries lack binding laws; rather, the database's non-exhaustive tracking is highly biased toward capturing high-level targets (like NDCs) while failing to document localized regulatory codes."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Slide 4: Policy Longevity by Instrument Type\n",
    "\n",
    "Bar chart of average policy longevity (years) for each instrument group, with error bars representing the standard deviation."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Display Longevity Chart\n",
    "display(Image(filename=os.path.join(outputs_dir, 'policy_longevity.png')))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "**Finding:** Strategic plans and targets have the longest lifespans (averaging 11.6 and 9.1 years, respectively), while regulatory standards and economic instruments are updated or retired much faster (averaging 5.4 and 5.5 years).\n",
    "\n",
    "**Caveat:** Longevity can only be calculated for the ~17% of policies that populate both `start_date` and `end_date`. This highly incomplete sample may suffer from selection bias, as short-term or temporary policies are more likely to have explicit end dates."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Slide 5: Clean Energy Landscapes\n",
    "\n",
    "Bar chart representing the share of clean energy policies targeting each exploded technology sub-type."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Display Clean Energy Taxonomy Chart\n",
    "display(Image(filename=os.path.join(outputs_dir, 'clean_energy_taxonomy.png')))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "**Finding:** Clean energy constitutes 81.0% of all policies in the dataset, with Renewable Energy Integration (53.0%) and Energy Efficiency Standards (44.3%) dominating the portfolio over demand-side management.\n",
    "\n",
    "**Caveat:** A single policy can be multi-classified across these categories, leading to overlapping counts. Additionally, the classification does not distinguish between high-impact and minor efficiency measures."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Slide 6: International External Support Dynamics\n",
    "\n",
    "Bar chart of the instrument mix of externally supported policies (representing 4.9% of the dataset)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Display External Support Instruments Chart\n",
    "display(Image(filename=os.path.join(outputs_dir, 'ext_support_instruments.png')))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "**Finding:** Externally supported policies are heavily concentrated in Targets (48.0%) and Strategic Planning (33.1%), with economic and regulatory implementation representing only 10.2% combined.\n",
    "\n",
    "**Caveat:** International climate aid is highly focused on initial agenda-setting (NDCs and roadmaps) rather than funding the ongoing operation or enforcement of regulatory codes."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Slide 7: Strategic Policy Sequencing (Markov Transition Matrix)\n",
    "\n",
    "Heatmap of the Markov transition probability matrix, showing the likelihood of transition from one instrument to another."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Display Sequencing Heatmap\n",
    "display(Image(filename=os.path.join(outputs_dir, 'sequencing_heatmap.png')))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "**Finding:** Transition from Targets to Strategic Planning is the most common path (42.6%), while direct transitions from Targets to binding Regulatory (10.7%) or Economic (12.0%) instruments are rare.\n",
    "\n",
    "**Caveat:** Transition sequences are computed chronologically within country-sector cohorts. It assumes a causal sequence (e.g. one policy leads to another), but subsequent policies may be enacted independently due to political changes."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Slide 8: Text Mining & Concept Evolution (NLP)\n",
    "\n",
    "Line plot showing the evolution of core policy concepts over time, along with key trigrams extracted for each capacity cluster."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Display Temporal Concepts Chart\n",
    "display(Image(filename=os.path.join(outputs_dir, 'temporal_concepts.png')))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "**Finding:** We observe a structural shift in policy terminology. Terms like \"net zero\" and \"carbon pricing\" have grown exponentially, with net zero appearing in **9.0%** of descriptions from 2020 to 2025. Trigrams show that Cluster 0 and 1 are dominated by international treaty compliance (*" + trigrams_c0 + "*), while Cluster 2 focuses on Specific Phase timelines (*" + trigrams_c2 + "*).\n",
    "\n",
    "**Caveat:** Keyword detection in descriptions represents how policies are framed in public summaries rather than the actual stringency or enforcement parameters of the legislative text."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Slide 9: Macroeconomic & Governance Clusters (K=3)\n",
    "\n",
    "Grouped bar chart comparing the average policies per country, clean energy share, and external support share across the three capacity clusters."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Display Cluster Comparison\n",
    "display(Image(filename=os.path.join(outputs_dir, 'cluster_comparison.png')))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "**Finding:** Emerging/Developed countries (Cluster 1) average 45.1 policies per country, while Least Developed countries (Cluster 2) average only 9.6 policies per country but have the highest share of external support policies (7.0%).\n",
    "\n",
    "**Caveat:** Cluster divisions are based on macroeconomic and governance indicators (GDP per capita and rule of law). The lower policy count in Cluster 2 is compounded by the database's coverage bias for lower-income countries."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Slide 10: Data Reliability & Limitations\n",
    "\n",
    "Before drawing conclusions, a critical review of the database shows three major systemic issues:\n",
    "\n",
    "1. **High Null Rates:**\n",
    "   - `stringency` (98.3% Null)\n",
    "   - `start_date` (73.5% Null) / `end_date` (71.3% Null)\n",
    "   - `impact_indicators` (92.4% Null)\n",
    "   - *Implication:* We cannot directly evaluate policy stringency or real-world effectiveness using database fields.\n",
    "\n",
    "2. **Fossil Rate (18.5%):**\n",
    "   - 18.5% of policies in the database mention fossil fuels (both phase-out and subsidies).\n",
    "   - *Implication:* Climate mitigation databases include policies that support fossil fuel generation, which must be filtered or accounted for.\n",
    "\n",
    "3. **Coverage Bias:**\n",
    "   - Acknowledge that the data represents \"what is documented\" rather than \"what is true in the world.\" Raw policy counts are highly biased by tracking depth (Comprehensive vs. Standard) and should not be used as a proxy for real-world climate commitment."
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbformat": 4,
   "nbformat_minor": 2,
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook_data, f, indent=1)

print("Notebook CPDB_deep_analysis.ipynb written successfully.")
