# src/data_management.py

import pandas as pd

def xlsx_to_csv(input_path, output_path):
    df = pd.read_excel(input_path)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    print(f"Saved: {output_path}")