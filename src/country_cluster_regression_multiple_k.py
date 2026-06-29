from pathlib import Path
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
COPILOT_DIR = ROOT / "notebooks" / "Shota Emoto" / "results" / "copilot"
COPILOT_DIR.mkdir(parents=True, exist_ok=True)


def load_avg_gdp_per_capita() -> pd.DataFrame:
    gdp_path = RAW_DIR / "GDP per capita" / "db9758b4-95e5-4584-b366-5dd38a5d3769_Data.csv"
    gdp = pd.read_csv(gdp_path)

    year_cols = [col for col in gdp.columns if re.search(r"(\d{4})", col)]
    year_cols = [col for col in year_cols if 2000 <= int(re.search(r"(\d{4})", col).group(1)) <= 2024]

    gdp_long = gdp[["Country Name", "Country Code"] + year_cols].copy()
    gdp_long = gdp_long.melt(
        id_vars=["Country Name", "Country Code"],
        value_vars=year_cols,
        var_name="year_col",
        value_name="gdp_pc",
    )
    gdp_long["year"] = gdp_long["year_col"].str.extract(r"(\d{4})").astype(int)
    gdp_long["gdp_pc"] = pd.to_numeric(gdp_long["gdp_pc"], errors="coerce")

    avg_gdp = (
        gdp_long[gdp_long["year"].between(2000, 2024)]
        .groupby("Country Code", as_index=False)["gdp_pc"]
        .mean()
        .rename(columns={"Country Code": "country_iso", "gdp_pc": "avg_gdp_pc"})
    )
    avg_gdp["country_iso"] = avg_gdp["country_iso"].astype(str).str.upper()
    return avg_gdp


def load_avg_rule_of_law() -> pd.DataFrame:
    rl_path = RAW_DIR / "rule of law indicator" / "rule_of_law.csv"
    rl = pd.read_csv(rl_path)
    rl = rl[rl["Year"].between(2000, 2024)].copy()
    rl["rule_law"] = pd.to_numeric(rl["Governance estimate (approx. -2.5 to +2.5)"], errors="coerce")

    avg_rl = (
        rl.groupby("Economy (code)", as_index=False)["rule_law"]
        .mean()
        .rename(columns={"Economy (code)": "country_iso", "rule_law": "avg_rule_law"})
    )
    avg_rl["country_iso"] = avg_rl["country_iso"].astype(str).str.upper()
    return avg_rl


def load_policy_investment() -> pd.DataFrame:
    policy_path = CLEAN_DIR / "merged_policy_investment_scores.csv"
    policy = pd.read_csv(policy_path)
    policy["country_iso"] = policy["country_iso"].astype(str).str.upper()
    return policy[[
        "country_iso",
        "clean_policy_count",
        "green_investment_narrow",
        "green_investment_broad",
        "green_share_narrow",
        "green_share_broad",
    ]].copy()


def prepare_data() -> pd.DataFrame:
    avg_gdp = load_avg_gdp_per_capita()
    avg_rl = load_avg_rule_of_law()
    policy = load_policy_investment()
    df = policy.merge(avg_gdp, on="country_iso", how="inner")
    df = df.merge(avg_rl, on="country_iso", how="inner")
    for col in ["avg_gdp_pc", "avg_rule_law", "clean_policy_count", "green_investment_narrow"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def assign_clusters(df: pd.DataFrame, n_clusters: int) -> pd.DataFrame:
    features = ["avg_gdp_pc", "avg_rule_law"]
    X = df[features].fillna(df[features].median())
    X_scaled = StandardScaler().fit_transform(X)
    labels = KMeans(n_clusters=n_clusters, random_state=42, n_init=50).fit_predict(X_scaled)
    out = df.copy()
    out["cluster"] = labels.astype(int)
    return out


def run_regressions(df: pd.DataFrame, n_clusters: int) -> tuple[pd.DataFrame, object, object, str]:
    df = df.copy()
    df["log_green"] = np.log1p(df["green_investment_narrow"])
    df["cluster"] = df["cluster"].astype(int)
    df = df.dropna(subset=["clean_policy_count", "log_green", "avg_gdp_pc", "avg_rule_law", "cluster"])

    base_formula = "log_green ~ clean_policy_count + avg_gdp_pc + avg_rule_law + C(cluster)"
    interaction_formula = "log_green ~ clean_policy_count + avg_gdp_pc + avg_rule_law + C(cluster)*clean_policy_count"

    base_model = smf.ols(formula=base_formula, data=df).fit(cov_type="HC3")
    interaction_model = smf.ols(formula=interaction_formula, data=df).fit(cov_type="HC3")

    cluster_summary = []
    for c in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == c]
        sub = sub[["clean_policy_count", "log_green"]].dropna()
        if len(sub) >= 2:
            corr = sub["clean_policy_count"].corr(sub["log_green"])
            slope = np.polyfit(sub["clean_policy_count"], sub["log_green"], 1)[0]
            cluster_summary.append((int(c), len(sub), corr, slope))

    summary_lines = [
        f"=== Cluster analysis for k={n_clusters} ===",
        f"N observations: {len(df)}",
        "",
        "Cluster-level correlation and slope:",
    ]
    for c, n, corr, slope in cluster_summary:
        summary_lines.append(f"cluster {c}: n={n}, corr={corr:.3f}, slope={slope:.3f}")
    summary_lines.extend(["", "Base regression summary:", base_model.summary().as_text(), "", "Interaction regression summary:", interaction_model.summary().as_text()])
    return df, base_model, interaction_model, "\n".join(summary_lines)


def plot_cluster_map(df: pd.DataFrame, n_clusters: int) -> None:
    plt.figure(figsize=(8, 6))
    sns.set(style="whitegrid")
    sns.scatterplot(data=df, x="avg_gdp_pc", y="avg_rule_law", hue="cluster", palette="tab10", s=80)
    centroids = df.groupby("cluster")[["avg_gdp_pc", "avg_rule_law"]].mean().reset_index()
    plt.scatter(centroids["avg_gdp_pc"], centroids["avg_rule_law"], c="black", s=140, marker="X")
    for _, row in centroids.iterrows():
        plt.text(row["avg_gdp_pc"], row["avg_rule_law"], f" C{int(row['cluster'])}", va="center")
    plt.xlabel("Average GDP per capita")
    plt.ylabel("Average Rule of Law")
    plt.title(f"Country clusters (k={n_clusters})")
    plt.legend(title="Cluster", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(COPILOT_DIR / f"cluster_map_k{n_clusters}.png", dpi=200)
    plt.close()


def plot_policy_vs_green(df: pd.DataFrame, n_clusters: int) -> None:
    plt.figure(figsize=(8, 6))
    sns.set(style="whitegrid")
    sns.scatterplot(data=df, x="clean_policy_count", y="log_green", hue="cluster", palette="tab10", s=70)
    x_min, x_max = int(df["clean_policy_count"].min()), int(df["clean_policy_count"].max())
    xs = np.linspace(x_min, x_max, 100)
    for c in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == c][["clean_policy_count", "log_green"]].dropna()
        if len(sub) < 2:
            continue
        slope, intercept = np.polyfit(sub["clean_policy_count"], sub["log_green"], 1)
        ys = slope * xs + intercept
        plt.plot(xs, ys, label=f"Cluster {int(c)} fit")
    plt.xlabel("Clean policy count")
    plt.ylabel("log(1 + green investment)")
    plt.title(f"Policy count vs log green investment (k={n_clusters})")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(COPILOT_DIR / f"policy_vs_green_k{n_clusters}.png", dpi=200)
    plt.close()


def main() -> None:
    df = prepare_data()
    for n_clusters in [3, 4, 5]:
        clustered = assign_clusters(df, n_clusters)
        clustered_df, base_model, interaction_model, summary_text = run_regressions(clustered, n_clusters)
        clustered_df.to_csv(COPILOT_DIR / f"country_cluster_regression_data_k{n_clusters}.csv", index=False)
        with (COPILOT_DIR / f"cluster_regression_summary_k{n_clusters}.txt").open("w", encoding="utf-8") as f:
            f.write(summary_text)
        plot_cluster_map(clustered_df, n_clusters)
        plot_policy_vs_green(clustered_df, n_clusters)

        with (COPILOT_DIR / f"interaction_regression_summary_k{n_clusters}.txt").open("w", encoding="utf-8") as f:
            f.write(interaction_model.summary().as_text())

        print(f"Finished k={n_clusters}")
        print(f"Saved outputs to {COPILOT_DIR}")


if __name__ == "__main__":
    main()
