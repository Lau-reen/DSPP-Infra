$ErrorActionPreference = 'Stop'
$repo = 'C:\Users\81809\OneDrive\ドキュメント\GitHub\DSPP-Infra'
Set-Location $repo
.\.venv\Scripts\python.exe src\country_cluster_regression_multiple_k.py
.\.venv\Scripts\python.exe src\plot_cluster_regressions.py
.\.venv\Scripts\python.exe src\export_markdown_report_to_pdf.py
