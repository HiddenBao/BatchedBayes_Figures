"""Post-process results CSV by rounding continuous process parameters.

Volume parameters (Oil_V, Surfactant_V, Cosurfactant_V) are volume percentages.
Sonication is time in minutes.
"""
import pandas as pd
import sys

ROUNDING = {
    "Oil_V":          2,
    "Surfactant_V":   2,
    "Cosurfactant_V": 2,
    "Sonication":     1,
}

def round_results(path: str) -> None:
    df = pd.read_csv(path)
    for col, decimals in ROUNDING.items():
        if col in df.columns:
            df[col] = df[col].round(decimals)
    df.to_csv(path, index=False)
    print(f"Rounded and saved: {path}")

if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "results/results_linear_Feno_Batch3.csv"
    round_results(csv_path)
