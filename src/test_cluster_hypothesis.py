import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'notebooks' / 'Shota Emoto' / 'results' / 'copilot' / 'country_cluster_regression_data.csv'
df = pd.read_csv(path)
df['log_green'] = np.log1p(pd.to_numeric(df['green_investment_narrow'], errors='coerce'))
df['clean_policy_count'] = pd.to_numeric(df['clean_policy_count'], errors='coerce')

print('Cluster averages:')
print(df.groupby('cluster')[['avg_gdp_pc', 'avg_rule_law', 'clean_policy_count', 'green_investment_narrow']].agg(['mean', 'std', 'count']).to_string())

print('\nCorrelations by cluster:')
for c in sorted(df['cluster'].dropna().unique()):
    sub = df[df['cluster'] == c]
    sub = sub[['clean_policy_count', 'log_green']].dropna()
    corr = sub['clean_policy_count'].corr(sub['log_green'])
    print(f'cluster {int(c)}: n={len(sub)}, corr={corr:.3f}')

print('\nSimple pooled correlation:')
pooled = df[['clean_policy_count', 'log_green']].dropna()
print(pooled['clean_policy_count'].corr(pooled['log_green']))
