import pandas as pd
import numpy as np

'''
File description:
This script loads the energy investment dataset from the specified CSV file,
computes overall and grouped descriptive statistics for the investment values,
and generates a Markdown report summarizing the results.
'''

def main():
    # Load dataset
    filepath = "ppi_energy.csv"
    print(f"Loading dataset from {filepath}...")
    df = pd.read_csv(filepath)
    
    # Check if investment_pp column is present
    if 'investment_pp' not in df.columns:
        print("Error: 'investment_pp' column not found in dataset.")
        return
    
    # Basic info
    total_rows = len(df)
    missing_investments = df['investment_pp'].isna().sum()
    valid_investments = df['investment_pp'].dropna()
    
    # Calculate overall descriptive statistics
    desc_stats = valid_investments.describe()
    
    # Calculate additional metrics
    median_val = valid_investments.median()
    sum_val = valid_investments.sum()
    
    # Print overall summary
    print("\n--- Overall Descriptive Statistics ---")
    print(f"Valid projects: {len(valid_investments)}")
    print(f"Missing values: {missing_investments}")
    print(f"Mean: {desc_stats['mean']}")
    print(f"Median: {median_val}")
    
    # Generate grouped statistics by Technology
    print("\n--- Descriptive Statistics by Technology ---")
    tech_summary = df.groupby('technology')['investment_pp'].agg(
        Count='count',
        Mean=lambda x: x.mean(),
        Median=lambda x: x.median(),
        StDev=lambda x: x.std(),
        Min='min',
        Max='max'
    ).reset_index()
    tech_summary = tech_summary.sort_values(by='Mean', ascending=False)
    
    # Generate grouped statistics by Country
    print("\n--- Descriptive Statistics by Country ---")
    country_summary = df.groupby('country')['investment_pp'].agg(
        Count='count',
        Mean=lambda x: x.mean(),
        Median=lambda x: x.median(),
        StDev=lambda x: x.std(),
        Min='min',
        Max='max'
    ).reset_index()
    country_summary = country_summary.sort_values(by='Mean', ascending=False)
    
    # Generate grouped statistics by Year
    print("\n--- Descriptive Statistics by Year ---")
    year_summary = df.groupby('year')['investment_pp'].agg(
        Count='count',
        Mean=lambda x: x.mean(),
        Median=lambda x: x.median(),
        StDev=lambda x: x.std(),
        Min='min',
        Max='max'
    ).reset_index()
    
    # Generate the Markdown file contents
    md_content = f"""# Investment Data Descriptive Statistics

This document presents a standard descriptive statistics analysis of the energy investment data from the World Bank Private Participation in Infrastructure (PPI) dataset (2010–2024), based on the cleaned `ppi_energy.csv` file.

The dataset contains a total of **{total_rows:,}** project records. Of these, **{len(valid_investments):,}** projects have valid investment figures, while **{missing_investments:,}** projects have missing investment values (reported as NaN or Not Available in the source data).

---

## 1. Overall Descriptive Statistics

Below is the standard descriptive statistics table for the `investment_pp` variable. Values are presented in raw numbers/USD and Millions USD for convenience.

| Statistic | Raw Value / Count | Value (Millions USD) | Description |
| :--- | :---: | :---: | :--- |
| **Count (Valid Projects)** | {len(valid_investments):,} | — | Number of projects with valid investment data |
| **Missing Values** | {missing_investments:,} | — | Number of projects without investment data |
| **Mean** | ${desc_stats['mean']:,.2f} | ${desc_stats['mean']/1e6:,.2f} M | Average investment size per project |
| **Standard Deviation** | ${desc_stats['std']:,.2f} | ${desc_stats['std']/1e6:,.2f} M | Spread/dispersion of project investments |
| **Minimum** | ${desc_stats['min']:,.2f} | ${desc_stats['min']/1e6:,.2f} M | Smallest recorded project investment |
| **25th Percentile** | ${desc_stats['25%']:,.2f} | ${desc_stats['25%']/1e6:,.2f} M | 25% of projects are below this investment value |
| **Median (50th Percentile)** | ${median_val:,.2f} | ${median_val/1e6:,.2f} M | Middle value of the investment distribution |
| **75th Percentile** | ${desc_stats['75%']:,.2f} | ${desc_stats['75%']/1e6:,.2f} M | 75% of projects are below this investment value |
| **Maximum** | ${desc_stats['max']:,.2f} | ${desc_stats['max']/1e6:,.2f} M | Largest recorded project investment |
| **Total Sum** | ${sum_val:,.2f} | ${sum_val/1e6:,.2f} M | Sum of all valid project investments |

---

## 2. Descriptive Statistics by Technology

The following table breaks down project investments by technology/source, sorted by mean investment size in descending order. (All values except Count are in Millions USD).

| Technology | Count | Mean (M USD) | Median (M USD) | StDev (M USD) | Min (M USD) | Max (M USD) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    
    for _, row in tech_summary.iterrows():
        mean_m = f"${row['Mean']/1e6:,.2f}" if not pd.isna(row['Mean']) else "N/A"
        med_m = f"${row['Median']/1e6:,.2f}" if not pd.isna(row['Median']) else "N/A"
        std_m = f"${row['StDev']/1e6:,.2f}" if not pd.isna(row['StDev']) else "N/A"
        min_m = f"${row['Min']/1e6:,.2f}" if not pd.isna(row['Min']) else "N/A"
        max_m = f"${row['Max']/1e6:,.2f}" if not pd.isna(row['Max']) else "N/A"
        md_content += f"| {row['technology']} | {int(row['Count']):,} | {mean_m} | {med_m} | {std_m} | {min_m} | {max_m} |\n"
        
    md_content += """
---

## 3. Descriptive Statistics by Country

The following table breaks down project investments by country (ISO3), sorted by mean investment size in descending order. (All values except Count are in Millions USD).

| Country | Count | Mean (M USD) | Median (M USD) | StDev (M USD) | Min (M USD) | Max (M USD) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
"""

    for _, row in country_summary.iterrows():
        mean_m = f"${row['Mean']/1e6:,.2f}" if not pd.isna(row['Mean']) else "N/A"
        med_m = f"${row['Median']/1e6:,.2f}" if not pd.isna(row['Median']) else "N/A"
        std_m = f"${row['StDev']/1e6:,.2f}" if not pd.isna(row['StDev']) else "N/A"
        min_m = f"${row['Min']/1e6:,.2f}" if not pd.isna(row['Min']) else "N/A"
        max_m = f"${row['Max']/1e6:,.2f}" if not pd.isna(row['Max']) else "N/A"
        md_content += f"| {row['country']} | {int(row['Count']):,} | {mean_m} | {med_m} | {std_m} | {min_m} | {max_m} |\n"

    md_content += """
---

## 4. Descriptive Statistics by Year

The following table shows the evolution of project counts and investment distributions over time (2010–2024). (All values except Count are in Millions USD).

| Year | Count | Mean (M USD) | Median (M USD) | StDev (M USD) | Min (M USD) | Max (M USD) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    
    for _, row in year_summary.iterrows():
        mean_m = f"${row['Mean']/1e6:,.2f}" if not pd.isna(row['Mean']) else "N/A"
        med_m = f"${row['Median']/1e6:,.2f}" if not pd.isna(row['Median']) else "N/A"
        std_m = f"${row['StDev']/1e6:,.2f}" if not pd.isna(row['StDev']) else "N/A"
        min_m = f"${row['Min']/1e6:,.2f}" if not pd.isna(row['Min']) else "N/A"
        max_m = f"${row['Max']/1e6:,.2f}" if not pd.isna(row['Max']) else "N/A"
        md_content += f"| {int(row['year'])} | {int(row['Count']):,} | {mean_m} | {med_m} | {std_m} | {min_m} | {max_m} |\n"
        
    # Write md file to the current directory
    output_md_path = "descriptive_statistics.md"
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"\nMarkdown report generated successfully at {output_md_path}")

if __name__ == "__main__":
    main()

