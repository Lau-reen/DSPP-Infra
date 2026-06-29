import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "data" / "clean"
COPILOT_DIR = ROOT / "notebooks" / "Shota Emoto" / "results" / "copilot"
COPILOT_DIR.mkdir(parents=True, exist_ok=True)
INPUT = COPILOT_DIR / "country_cluster_regression_data.csv"
if not INPUT.exists():
    INPUT = CLEAN_DIR / "country_cluster_regression_data.csv"
OUT1 = COPILOT_DIR / "cluster_gdp_rule_scatter.png"
OUT2 = COPILOT_DIR / "policy_vs_green_by_cluster_log.png"
OUT3 = COPILOT_DIR / "policy_vs_green_by_cluster_raw.png"
OUT4 = COPILOT_DIR / "policy_vs_green_regression_comparison.txt"


def plot_gdp_rule(df):
    plt.figure(figsize=(8,6))
    sns.set(style="whitegrid")
    scatter = sns.scatterplot(
        data=df, x="avg_gdp_pc", y="avg_rule_law", hue="cluster", palette="tab10", s=80
    )
    # centroids
    centroids = df.groupby("cluster")[['avg_gdp_pc','avg_rule_law']].mean().reset_index()
    plt.scatter(centroids['avg_gdp_pc'], centroids['avg_rule_law'], c='black', s=120, marker='X')
    for _, row in centroids.iterrows():
        plt.text(row['avg_gdp_pc'], row['avg_rule_law'], f"  C{int(row['cluster'])}", va='center')

    plt.xlabel('Average GDP per capita (2000-2024)')
    plt.ylabel('Average Rule of Law (WGI)')
    plt.title('Country clusters: GDP per capita vs Rule of Law')
    plt.legend(title='Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUT1, dpi=200)
    plt.close()


def plot_policy_vs_green(df):
    # ensure numeric
    df['clean_policy_count'] = pd.to_numeric(df['clean_policy_count'], errors='coerce')
    df['green_investment_narrow'] = pd.to_numeric(df['green_investment_narrow'], errors='coerce')
    df['log_green'] = np.log1p(df['green_investment_narrow'])

    plt.figure(figsize=(8,6))
    sns.set(style="whitegrid")

    # scatter
    sns.scatterplot(data=df, x='clean_policy_count', y='log_green', hue='cluster', palette='tab10', s=70)

    # per-cluster regression lines
    clusters = sorted(df['cluster'].dropna().unique())
    x_min, x_max = int(df['clean_policy_count'].min()), int(df['clean_policy_count'].max())
    xs = np.linspace(x_min, x_max, 100)
    for c in clusters:
        sub = df[df['cluster']==c]
        if len(sub) < 2:
            continue
        # fit linear model on x and log_green
        ok = sub[['clean_policy_count','log_green']].dropna()
        if ok.shape[0] < 2:
            continue
        coef = np.polyfit(ok['clean_policy_count'], ok['log_green'], 1)
        ys = coef[0]*xs + coef[1]
        plt.plot(xs, ys, label=f'Cluster {int(c)} fit')

    plt.xlabel('Clean policy count')
    plt.ylabel('log(1 + green investment)')
    plt.title('Policy count vs log green investment, by cluster')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUT2, dpi=200)
    plt.close()


def main():
    df = pd.read_csv(INPUT)
    plot_gdp_rule(df)
    plot_policy_vs_green(df)

    # also create raw (no-log) plot
    # ensure numeric
    df['clean_policy_count'] = pd.to_numeric(df['clean_policy_count'], errors='coerce')
    df['green_investment_narrow'] = pd.to_numeric(df['green_investment_narrow'], errors='coerce')

    # raw scatter + per-cluster fits
    plt.figure(figsize=(8,6))
    sns.set(style="whitegrid")
    sns.scatterplot(data=df, x='clean_policy_count', y='green_investment_narrow', hue='cluster', palette='tab10', s=70)
    clusters = sorted(df['cluster'].dropna().unique())
    x_min, x_max = int(df['clean_policy_count'].min()), int(df['clean_policy_count'].max())
    xs = np.linspace(x_min, x_max, 100)
    for c in clusters:
        sub = df[df['cluster']==c]
        ok = sub[['clean_policy_count','green_investment_narrow']].dropna()
        if ok.shape[0] < 2:
            continue
        coef = np.polyfit(ok['clean_policy_count'], ok['green_investment_narrow'], 1)
        ys = coef[0]*xs + coef[1]
        plt.plot(xs, ys, label=f'Cluster {int(c)} fit')

    plt.xlabel('Clean policy count')
    plt.ylabel('green investment (narrow, raw)')
    plt.title('Policy count vs green investment (raw), by cluster')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUT3, dpi=200)
    plt.close()

    # run and save OLS comparisons (log vs raw)
    # drop NA rows for regression
    reg_df = df[['clean_policy_count','avg_gdp_pc','avg_rule_law','cluster','green_investment_narrow']].copy()
    reg_df['log_green'] = np.log1p(reg_df['green_investment_narrow'])
    reg_df = reg_df.dropna()

    formulas = {
        'log_green': 'log_green ~ clean_policy_count + avg_gdp_pc + avg_rule_law + C(cluster)',
        'raw_green': 'green_investment_narrow ~ clean_policy_count + avg_gdp_pc + avg_rule_law + C(cluster)'
    }
    summaries = []
    for name, formula in formulas.items():
        try:
            mod = smf.ols(formula=formula, data=reg_df).fit(cov_type='HC3')
            summaries.append(f"=== Regression: {name} ===\n")
            summaries.append(mod.summary().as_text())
            summaries.append('\n\n')
        except Exception as e:
            summaries.append(f"Regression {name} failed: {e}\n\n")

    with open(OUT4, 'w', encoding='utf-8') as f:
        f.writelines(summaries)

    print('Saved plots:')
    print(OUT1)
    print(OUT2)
    print(OUT3)
    print(OUT4)

if __name__ == '__main__':
    main()
