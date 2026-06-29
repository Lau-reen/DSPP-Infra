from pathlib import Path
import re

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"


def load_avg_gdp_per_capita() -> pd.DataFrame:
    gdp_path = RAW_DIR / "GDP per capita" / "db9758b4-95e5-4584-b366-5dd38a5d3769_Data.csv"
    gdp = pd.read_csv(gdp_path)

    year_cols = [col for col in gdp.columns if re.search(r"(\d{4})", col)]
    year_cols = [
        col for col in year_cols if 2000 <= int(re.search(r"(\d{4})", col).group(1)) <= 2024
    ]

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
    rl["rule_law"] = pd.to_numeric(
        rl["Governance estimate (approx. -2.5 to +2.5)"], errors="coerce"
    )

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
    return policy[
        [
            "country_iso",
            "clean_policy_count",
            "green_investment_narrow",
            "green_investment_broad",
            "green_share_narrow",
            "green_share_broad",
        ]
    ].copy()


def cluster_countries(df: pd.DataFrame) -> pd.DataFrame:
    features = ["avg_gdp_pc", "avg_rule_law"]
    X = df[features].fillna(df[features].median())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    best_k = 2
    best_score = -1
    for k in range(2, 6):
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        if score > best_score:
            best_score = score
            best_k = k

    df = df.copy()
    df["cluster"] = KMeans(n_clusters=best_k, random_state=42, n_init=20).fit_predict(X_scaled)
    return df


def run_regression(df: pd.DataFrame) -> tuple[pd.DataFrame, object]:
    df = df.copy()
    for col in ["clean_policy_count", "green_investment_narrow", "avg_gdp_pc", "avg_rule_law", "cluster"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[["avg_gdp_pc", "avg_rule_law", "green_investment_narrow"]] = df[
        ["avg_gdp_pc", "avg_rule_law", "green_investment_narrow"]
    ].fillna(0)
    df["cluster"] = df["cluster"].fillna(0).astype(int)
    df["log_green_investment"] = np.log1p(df["green_investment_narrow"])

    X = pd.get_dummies(
        df[["clean_policy_count", "avg_gdp_pc", "avg_rule_law", "cluster"]],
        columns=["cluster"],
        drop_first=True,
    ).astype(float)
    X = sm.add_constant(X)
    y = df["log_green_investment"]

    model = sm.OLS(y, X).fit()
    return df, model


def main() -> None:
    avg_gdp = load_avg_gdp_per_capita()
    avg_rl = load_avg_rule_of_law()
    policy = load_policy_investment()

    df = policy.merge(avg_gdp, on="country_iso", how="inner")
    df = df.merge(avg_rl, on="country_iso", how="inner")
    df = cluster_countries(df)
    df, model = run_regression(df)

    output_path = CLEAN_DIR / "country_cluster_regression_data.csv"
    df.to_csv(output_path, index=False)

    summary_path = CLEAN_DIR / "country_cluster_regression_summary.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write(str(model.summary()))

    print(f"Saved clustered dataset to: {output_path}")
    print(f"Saved regression summary to: {summary_path}")
    print("\nRegression summary:")
    print(model.summary())


if __name__ == "__main__":
    main()
from pathlib import Path
import re

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"


def load_avg_gdp_per_capita() -> pd.DataFrame:
    gdp_path = RAW_DIR / "GDP per capita" / "db9758b4-95e5-4584-b366-5dd38a5d3769_Data.csv"
    gdp = pd.read_csv(gdp_path)

    year_cols = [col for col in gdp.columns if re.search(r"(\d{4})", col)]
    year_cols = [
        col for col in year_cols if 2000 <= int(re.search(r"(\d{4})", col).group(1)) <= 2024
    ]

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
    rl["rule_law"] = pd.to_numeric(
        rl["Governance estimate (approx. -2.5 to +2.5)"], errors="coerce"
    )

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
    return policy[
        [
            "country_iso",
            "clean_policy_count",
            "green_investment_narrow",
            "green_investment_broad",
            "green_share_narrow",
            "green_share_broad",
        ]
    ].copy()


def cluster_countries(df: pd.DataFrame) -> pd.DataFrame:
    features = ["avg_gdp_pc", "avg_rule_law"]
    X = df[features].fillna(df[features].median())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    best_k = 2
    best_score = -1
    for k in range(2, 6):
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        if score > best_score:
            best_score = score
            best_k = k

    df = df.copy()
    df["cluster"] = KMeans(n_clusters=best_k, random_state=42, n_init=20).fit_predict(X_scaled)
    return df


def run_regression(df: pd.DataFrame) -> tuple[pd.DataFrame, object]:
    df = df.copy()
    for col in ["clean_policy_count", "green_investment_narrow", "avg_gdp_pc", "avg_rule_law", "cluster"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[["avg_gdp_pc", "avg_rule_law", "green_investment_narrow"]] = df[
        ["avg_gdp_pc", "avg_rule_law", "green_investment_narrow"]
    ].fillna(0)
    df["cluster"] = df["cluster"].fillna(0).astype(int)
    df["log_green_investment"] = np.log1p(df["green_investment_narrow"])

    X = pd.get_dummies(
        df[["clean_policy_count", "avg_gdp_pc", "avg_rule_law", "cluster"]],
        columns=["cluster"],
        drop_first=True,
    ).astype(float)
    X = sm.add_constant(X)
    y = df["log_green_investment"]

    model = sm.OLS(y, X).fit()
    return df, model


def main() -> None:
    avg_gdp = load_avg_gdp_per_capita()
    avg_rl = load_avg_rule_of_law()
    policy = load_policy_investment()

    df = policy.merge(avg_gdp, on="country_iso", how="inner")
    df = df.merge(avg_rl, on="country_iso", how="inner")
    df = cluster_countries(df)
    df, model = run_regression(df)

    output_path = CLEAN_DIR / "country_cluster_regression_data.csv"
    df.to_csv(output_path, index=False)

    summary_path = CLEAN_DIR / "country_cluster_regression_summary.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write(str(model.summary()))

    print(f"Saved clustered dataset to: {output_path}")
    print(f"Saved regression summary to: {summary_path}")
    print("\nRegression summary:")
    print(model.summary())


if __name__ == "__main__":
    main()
from pathlib import Path
import re
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"


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
    rl["rule_law"] = pd.to_numeric(
        rl["Governance estimate (approx. -2.5 to +2.5)"], errors="coerce"
    )

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


def cluster_countries(df: pd.DataFrame) -> pd.DataFrame:
    features = ["avg_gdp_pc", "avg_rule_law"]
    X = df[features].fillna(df[features].median())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    best_k = None
    best_score = -1
    for k in range(2, 6):
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        if score > best_score:
            best_score = score
            best_k = k

    df = df.copy()
    df["cluster"] = KMeans(n_clusters=best_k, random_state=42, n_init=20).fit_predict(X_scaled)
    return df


def run_regression(df: pd.DataFrame) -> tuple[pd.DataFrame, object]:
    df = df.copy()
    for col in ["clean_policy_count", "green_investment_narrow", "avg_gdp_pc", "avg_rule_law", "cluster"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[["avg_gdp_pc", "avg_rule_law", "green_investment_narrow"]] = df[
        ["avg_gdp_pc", "avg_rule_law", "green_investment_narrow"]
    ].fillna(0)
    df["cluster"] = df["cluster"].fillna(0).astype(int)
    df["log_green_investment"] = np.log1p(df["green_investment_narrow"])

    X = pd.get_dummies(
        df[["clean_policy_count", "avg_gdp_pc", "avg_rule_law", "cluster"]],
        columns=["cluster"],
        drop_first=True,
    ).astype(float)
    X = sm.add_constant(X)
    y = df["log_green_investment"]

    model = sm.OLS(y, X).fit()
    return df, model


def main() -> None:
    avg_gdp = load_avg_gdp_per_capita()
    avg_rl = load_avg_rule_of_law()
    policy = load_policy_investment()

    df = policy.merge(avg_gdp, on="country_iso", how="inner")
    df = df.merge(avg_rl, on="country_iso", how="inner")
    df = cluster_countries(df)
    df, model = run_regression(df)

    output_path = CLEAN_DIR / "country_cluster_regression_data.csv"
    df.to_csv(output_path, index=False)

    summary_path = CLEAN_DIR / "country_cluster_regression_summary.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write(str(model.summary()))

    print(f"Saved clustered dataset to: {output_path}")
    print(f"Saved regression summary to: {summary_path}")
    print("\nRegression summary:")
    print(model.summary())


if __name__ == "__main__":
    main()
from pathlib import Path
import re
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"


def load_avg_gdp_per_capita() -> pd.DataFrame:
    gdp_path = RAW_DIR / "GDP per capita" / "db9758b4-95e5-4584-b366-5dd38a5d3769_Data.csv"
    gdp = pd.read_csv(gdp_path)

    year_cols = [
        col
        for col in gdp.columns
        if re.search(r"(\d{4})", col)
    ]
    year_cols = [
        col for col in year_cols
        if 2000 <= int(re.search(r"(\d{4})", col).group(1)) <= 2024
    ]

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
    rl["rule_law"] = pd.to_numeric(
        rl["Governance estimate (approx. -2.5 to +2.5)"], errors="coerce"
    )

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


def cluster_countries(df: pd.DataFrame) -> pd.DataFrame:
    features = ["avg_gdp_pc", "avg_rule_law"]
    X = df[features].fillna(df[features].median())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    best_k = None
    best_score = -1
    for k in range(2, 6):
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        if score > best_score:
            best_score = score
            best_k = k

    final_model = KMeans(n_clusters=best_k, random_state=42, n_init=20)
    df = df.copy()
    df["cluster"] = final_model.fit_predict(X_scaled)
    return df


def run_regression(df: pd.DataFrame) -> tuple[pd.DataFrame, object]:
    df = df.copy()
    df["log_green_investment"] = np.log1p(df["green_investment_narrow"])

    X = pd.get_dummies(
        df[["clean_policy_count", "avg_gdp_pc", "avg_rule_law", "cluster"]],
        columns=["cluster"],
        drop_first=True,
    )
    X = sm.add_constant(X)
    y = df["log_green_investment"]

    model = sm.OLS(y, X).fit()
    return df, model


def main() -> None:
    avg_gdp = load_avg_gdp_per_capita()
    avg_rl = load_avg_rule_of_law()
    policy = load_policy_investment()

    df = policy.merge(avg_gdp, on="country_iso", how="inner")
    df = df.merge(avg_rl, on="country_iso", how="inner")

    df = cluster_countries(df)
    df, model = run_regression(df)

    output_path = CLEAN_DIR / "country_cluster_regression_data.csv"
    df.to_csv(output_path, index=False)

    summary_path = CLEAN_DIR / "country_cluster_regression_summary.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write(str(model.summary()))

    print(f"Saved clustered dataset to: {output_path}")
    print(f"Saved regression summary to: {summary_path}")
    print("\nRegression summary:")
    print(model.summary())


if __name__ == "__main__":
    main()
