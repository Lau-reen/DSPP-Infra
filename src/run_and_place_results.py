import subprocess
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
COPILOT_DIR = ROOT / "notebooks" / "Shota Emoto" / "results" / "copilot"
COPILOT_DIR.mkdir(parents=True, exist_ok=True)

# Scripts to run
SCRIPTS = [
    ROOT / "src" / "country_cluster_regression.py",
    ROOT / "src" / "plot_cluster_regressions.py",
]

# Run scripts
for script in SCRIPTS:
    print(f"Running: {script}")
    subprocess.run(["python", str(script)], check=False)

# Move expected output files from data/clean to COPILOT_DIR if they exist
DATA_CLEAN = ROOT / "data" / "clean"
PATTERNS = [
    "cluster_gdp_rule_scatter.png",
    "policy_vs_green_by_cluster*.png",
    "country_cluster_regression_data.csv",
    "country_cluster_regression_summary.txt",
    "policy_vs_green_regression_comparison.txt",
]

moved = []
for pat in PATTERNS:
    for p in DATA_CLEAN.glob(pat):
        dest = COPILOT_DIR / p.name
        try:
            shutil.move(str(p), str(dest))
            moved.append(dest)
        except Exception as e:
            print(f"Failed to move {p} -> {dest}: {e}")

print("Moved files:")
for m in moved:
    print(m)

print("All done. Outputs are in:")
print(COPILOT_DIR)
