from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
TEMP_DIR = DATA_DIR / "temp"
REPORTS_DIR = ROOT_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

def classify_technology(tech):
    # Standard classification based on ppi_green_share_methodology.md
    green_techs = {
        'Solar, PV', 'Solar, CSP', 'Solar, CPV', 'Solar, PV, N/A', 'Solar, PV, Not Applicable',
        'Wind', 'Wind, N/A', 'Wind, Not Applicable', 'Wind, Solar, PV', 'Solar, PV, Wind',
        'Solar, PV, Wind, N/A', 'Solar, PV, Solar, PV', 'Solar, PV, Biogas',
        'Hydro, Small (<50MW)', 'Geothermal', 'Biomass', 'Biogas'
    }
    brown_techs = {
        'Coal', 'Natural Gas', 'Diesel', 'Steam',
        'Natural Gas, Diesel', 'Diesel, Natural Gas', 'Natural Gas, Steam'
    }
    broad_extra = {'Hydro, Large (>50MW)', 'Waste'}

    tech_str = str(tech).strip()
    if tech_str in green_techs:
        return 1, 1  # is_green=1 (narrow), is_green_broad=1 (broad)
    elif tech_str in brown_techs:
        return 0, 0  # is_green=0 (narrow), is_green_broad=0 (broad)
    elif tech_str in broad_extra:
        return np.nan, 1  # is_green=NaN (narrow), is_green_broad=1 (broad)
    else:
        return np.nan, np.nan  # noise/hybrid to be dropped

def main():
    print("Step 1: Processing CPDB Policy Data...")
    cpdb = pd.read_csv(RAW_DIR / "cpdb_country_all.csv")
    
    # Filter jurisdiction to National or Country
    if 'National' in cpdb['jurisdiction'].unique():
        df_policies = cpdb[cpdb['jurisdiction'] == 'National'].copy()
    else:
        df_policies = cpdb[cpdb['jurisdiction'] == 'Country'].copy()
        
    # Filter status: In force
    df_policies = df_policies[df_policies['policy_status'] == 'In force'].copy()
    
    # Parse dates
    df_policies['start_date'] = pd.to_numeric(df_policies['start_date'], errors='coerce')
    df_policies['end_date'] = pd.to_numeric(df_policies['end_date'], errors='coerce')
    
    # Lagged policy period: cumulative up to 2022
    # In force between 2014 and 2022
    cond_start = df_policies['start_date'].isna() | (df_policies['start_date'] <= 2022)
    cond_end = df_policies['end_date'].isna() | (df_policies['end_date'] >= 2014)
    df_policies_filtered = df_policies[cond_start & cond_end].copy()
    
    # Classify Clean Energy Policies
    # Using structured columns: policy_type and sector
    df_policies_filtered['is_clean_energy'] = (
        df_policies_filtered['policy_type'].fillna("").str.contains('Renewables|Energy efficiency', case=False) |
        df_policies_filtered['sector'].fillna("").str.contains('Renewables|Electricity', case=False)
    ).astype(int)
    
    # Save the annotated clean energy policies
    df_policies_filtered.to_csv(CLEAN_DIR / "cpdb_green_annotated.csv", index=False)
    print("Saved annotated clean energy policies to cpdb_green_annotated.csv")
    
    # Group policies by country and count total vs clean energy
    policy_summary = []
    for country_iso, group in df_policies_filtered.groupby('country_iso'):
        country_name = group['country'].iloc[0] if 'country' in group.columns else ''
        total_p = len(group)
        clean_p = group['is_clean_energy'].sum()
        share_p = clean_p / total_p if total_p > 0 else 0.0
        policy_summary.append({
            'country_iso': country_iso,
            'country': country_name,
            'clean_policy_count': int(clean_p),
            'total_policy_count': total_p,
            'green_policy_share': share_p
        })
    df_policy_scores = pd.DataFrame(policy_summary)
    
    # Save country-level green scores file
    df_green_scores = df_policy_scores.sort_values(by=['clean_policy_count', 'country'], ascending=[False, True])
    df_green_scores.to_csv(CLEAN_DIR / "country_green_scores.csv", index=False)
    print("Saved country-level green scores to country_green_scores.csv")
    
    print(f"Processed policy scores for {len(df_policy_scores)} countries.")

    print("\nStep 2: Processing PPI Investment Data...")
    ppi = pd.read_csv(TEMP_DIR / "ppi_energy.csv")
    
    # Apply technology classification
    classifications = ppi['technology'].apply(classify_technology)
    ppi['is_green'] = [c[0] for c in classifications]
    ppi['is_green_broad'] = [c[1] for c in classifications]
    
    # Focus investment period: 2016 to 2024 (2-year lag from 2014-2022 policy window)
    ppi_filtered = ppi[(ppi['year'] >= 2016) & (ppi['year'] <= 2024)].copy()
    
    # Convert investments to millions USD for convenience
    ppi_filtered['investment_m'] = ppi_filtered['investment_pp'] / 1_000_000
    
    # Aggregate investments per country
    investments_summary = []
    for country, group in ppi_filtered.groupby('country'):
        # Narrow definition
        narrow_group = group.dropna(subset=['is_green'])
        total_inv_narrow = narrow_group['investment_m'].sum()
        green_inv_narrow = narrow_group[narrow_group['is_green'] == 1]['investment_m'].sum()
        share_inv_narrow = green_inv_narrow / total_inv_narrow if total_inv_narrow > 0 else 0.0
        
        # Broad definition
        broad_group = group.dropna(subset=['is_green_broad'])
        total_inv_broad = broad_group['investment_m'].sum()
        green_inv_broad = broad_group[broad_group['is_green_broad'] == 1]['investment_m'].sum()
        share_inv_broad = green_inv_broad / total_inv_broad if total_inv_broad > 0 else 0.0
        
        investments_summary.append({
            'country_iso': country,
            'total_investment_narrow': total_inv_narrow,
            'green_investment_narrow': green_inv_narrow,
            'green_share_narrow': share_inv_narrow,
            'total_investment_broad': total_inv_broad,
            'green_investment_broad': green_inv_broad,
            'green_share_broad': share_inv_broad
        })
    df_investments = pd.DataFrame(investments_summary)
    print(f"Processed investments for {len(df_investments)} countries.")

    print("\nStep 3: Merging Policy and Investment Datasets...")
    # Inner join to only match countries with both policy and investment data
    merged = pd.merge(df_policy_scores, df_investments, on='country_iso')
    print(f"Merged dataset contains {len(merged)} countries.")
    
    # Save merged dataset for transparency
    merged.to_csv(CLEAN_DIR / "merged_policy_investment_scores.csv", index=False)
    print("Saved merged dataset to merged_policy_investment_scores.csv")

    print("\nStep 4: Generating Replicated Figures...")
    sns.set_theme(style="whitegrid")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot A: Clean Energy Policy Count vs Green Investment Share (Narrow)
    sns.regplot(data=merged, x='clean_policy_count', y='green_share_narrow', ax=axes[0, 0],
                scatter_kws={'alpha':0.6, 'color':'#2ca02c'}, line_kws={'color':'red'})
    axes[0, 0].set_title("A. Clean Energy Policy Count vs. Green Share (Narrow)", fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel("Clean Energy Policy Count (Cumulative up to 2022)")
    axes[0, 0].set_ylabel("Green Share of Energy Investments (2016-2024)")
    
    # Plot B: Green Policy Share vs Green Investment Share (Narrow)
    sns.regplot(data=merged, x='green_policy_share', y='green_share_narrow', ax=axes[0, 1],
                scatter_kws={'alpha':0.6, 'color':'#1f77b4'}, line_kws={'color':'red'})
    axes[0, 1].set_title("B. Green Policy Share vs. Green Share (Narrow)", fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel("Green Policy Share (Proportion of Climate Policies up to 2022)")
    axes[0, 1].set_ylabel("Green Share of Energy Investments (2016-2024)")

    # Plot C: Clean Energy Policy Count vs Absolute Green Investment (Narrow)
    sns.regplot(data=merged, x='clean_policy_count', y='green_investment_narrow', ax=axes[1, 0],
                scatter_kws={'alpha':0.6, 'color':'#9467bd'}, line_kws={'color':'red'})
    axes[1, 0].set_title("C. Clean Policy Count vs. Absolute Green Investment (Narrow)", fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel("Clean Energy Policy Count (Cumulative up to 2022)")
    axes[1, 0].set_ylabel("Absolute Green Investment (USD Millions, 2016-2024)")

    # Plot D: Green Policy Share vs Absolute Green Investment (Narrow)
    sns.regplot(data=merged, x='green_policy_share', y='green_investment_narrow', ax=axes[1, 1],
                scatter_kws={'alpha':0.6, 'color':'#ff7f0e'}, line_kws={'color':'red'})
    axes[1, 1].set_title("D. Green Policy Share vs. Absolute Green Investment (Narrow)", fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel("Green Policy Share (Proportion of Climate Policies up to 2022)")
    axes[1, 1].set_ylabel("Absolute Green Investment (USD Millions, 2016-2024)")

    # Label top 10 countries with largest green investments to provide signal
    top_countries = merged.nlargest(10, 'green_investment_narrow')
    for ax_idx, ax in enumerate(axes.flat):
        x_col = 'clean_policy_count' if ax_idx in [0, 2] else 'green_policy_share'
        y_col = 'green_share_narrow' if ax_idx in [0, 1] else 'green_investment_narrow'
        for idx, row in top_countries.iterrows():
            ax.text(row[x_col] + (0.5 if x_col=='clean_policy_count' else 0.01),
                    row[y_col],
                    row['country_iso'], fontsize=9, alpha=0.8, weight='semibold')

    plt.tight_layout()
    plot_path = REPORTS_DIR / "clean_energy_replication_plots.png"
    plt.savefig(plot_path, dpi=300)
    print(f"Figures saved successfully to {plot_path}")
    
    # Calculate correlations
    print("\nCorrelation matrix (Pearson) between policies and narrow investments:")
    print(merged[['clean_policy_count', 'green_policy_share', 'green_investment_narrow', 'green_share_narrow']].corr())

if __name__ == "__main__":
    main()
