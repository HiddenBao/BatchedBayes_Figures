"""
Score every row in the microemulsion dataset using the objective function
from applications.py, and report per-target component scores alongside the
final objective value.
"""

import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "BayesianOptimization"))
from applications import MicroemulsionFormulation


def compute_component_scores(preds: np.ndarray) -> pd.DataFrame:
    """Return a DataFrame of each intermediate score and the final objective."""
    size = preds[:, 0]
    pdi  = preds[:, 1]
    zeta = preds[:, 2]
    sep  = preds[:, 3]
    dl   = preds[:, 4]
    perm = preds[:, 5]

    size_score = np.maximum(0.0, (size - 100.0) / 900.0)

    pdi_score = np.where(
        pdi >= 0.1,
        (pdi - 0.1) / 0.9,
        -(0.1 - pdi) / (0.9 * 5.0),
    )

    zeta_score = np.maximum(0.0, (np.abs(zeta) - 10.0) / 10.0)

    dl_dist = np.abs(dl - 100.0)
    dl_score = np.where(
        np.isnan(dl), 0.0,
        np.where(
            dl_dist <= 5.0,
            dl_dist / 130.0,
            5.0 / 130.0 + (dl_dist - 5.0) / 26.0,
        ),
    )

    perm_score = np.where(
        np.isnan(perm), 0.0,
        np.where(
            perm <= 20e-6,
            (20e-6 - perm) / 20e-6,
            -(perm - 20e-6) / (20e-6 * 5.0),
        ),
    )

    formulation_loss = (
        3.0 * size_score
        + 2.0 * pdi_score
        + 1.0 * zeta_score
        + 2.0 * dl_score
        + 3.0 * perm_score
    )
    stability = 1.0 - np.clip(sep, 0.0, 1.0)
    objective = formulation_loss / np.maximum(stability, 0.01)

    return pd.DataFrame({
        "size_score (w=3)":  size_score,
        "pdi_score  (w=2)":  pdi_score,
        "zeta_score (w=1)":  zeta_score,
        "dl_score   (w=2)":  dl_score,
        "perm_score (w=3)":  perm_score,
        "formulation_loss":  formulation_loss,
        "stability_factor":  stability,
        "objective":         objective,
    })


def main():
    app = MicroemulsionFormulation()
    raw = pd.read_csv(app.dataset_path)

    output_cols = app.output_headers  # [Droplet_Size, PDI, Zeta_P, Phase_Sep, Drug_Loading, Permeability]

    # Only score formulations with all outputs measured; blank (no-API) rows
    # lack Drug_Loading/Permeability and are excluded. DoE screening rows are
    # excluded too (DoE-OPT has a full output set but is a baseline, not a
    # Campaign 2 formulation) -- see analysis/build_score_datasets.py.
    complete = raw[output_cols].notna().all(axis=1) & ~raw["Exp"].str.startswith("DoE")
    print(f"Excluding {(~complete).sum()} rows with missing outputs; scoring {complete.sum()} rows.")
    raw = raw[complete].reset_index(drop=True)

    preds = raw[output_cols].to_numpy(dtype=float)

    scores = compute_component_scores(preds)

    id_cols = ["Exp", "Rep", "Oil", "Surfactant", "Cosurfactant", "API_Name",
               "Oil_V", "Surfactant_V", "Cosurfactant_V", "Sonication"]
    id_cols = [c for c in id_cols if c in raw.columns]

    result = pd.concat([raw[id_cols], raw[output_cols].reset_index(drop=True), scores.reset_index(drop=True)], axis=1)
    result = result.sort_values("objective", ascending=True).reset_index(drop=True)  # best (lowest) first

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.float_format", "{:.4f}".format)

    print("=" * 120)
    print(f"Dataset: {app.dataset_path}")
    print(f"Rows: {len(result)}  |  Output columns: {output_cols}")
    print("=" * 120)
    print(result.to_string(index=False))

    print("\n" + "=" * 60)
    print("Summary statistics — objective column")
    print("=" * 60)
    print(result["objective"].describe().to_string())

    top5 = result.nsmallest(5, "objective")[id_cols + ["objective"]]
    print("\nTop-5 lowest (best) objective rows:")
    print(top5.to_string(index=False))

    out_path = os.path.join(os.path.dirname(__file__), "analysis", "datasets", "campaign2_scores.csv")
    result.to_csv(out_path, index=False)
    print(f"\nFull table saved to: {out_path}")


if __name__ == "__main__":
    main()
