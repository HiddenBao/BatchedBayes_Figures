import logging
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer
from sklearn.compose import ColumnTransformer

logger = logging.getLogger(__name__)


class MicroemulsionFormulation:
    def __init__(self):
        self.dataset_path = os.path.join(
            os.path.dirname(__file__), "data", "MicroemulsionFormulation_Comprehensive.csv"
        )
        self.hlb_path = os.path.join(
            os.path.dirname(__file__), "data", "hlb_values.csv"
        )
        self.oil_surf_path = os.path.join(
            os.path.dirname(__file__), "data", "oil_surfactant_compatibility.csv"
        )
        self.oil_cosurf_path = os.path.join(
            os.path.dirname(__file__), "data", "oil_cosurfactant_compatibility.csv"
        )
        self.surf_cosurf_path = os.path.join(
            os.path.dirname(__file__), "data", "surfactant_cosurfactant_compatibility.csv"
        )
        self.solubility_path = os.path.join(
            os.path.dirname(__file__), "data", "solubility_values.csv"
        )
        self.input_headers = [
            "Oil_V",
            "Surfactant_V",
            "Cosurfactant_V",
            "Sonication",
            "Oil",
            "Surfactant",
            "Cosurfactant",
            "API_Name",
        ]
        self.category_headers = [
            "Oil",
            "Surfactant",
            "Cosurfactant",
            "API_Name",
        ]
        self.descriptor_headers = [
            'hlb_oil',
            'hlb_surfactant',
            'hlb_cosurfactant',
            'oil_surf_compat',
            'oil_cosurf_compat',
            'surf_cosurf_compat',
            'solubility_oil',
            'solubility_surfactant',
            'solubility_cosurfactant',
        ]
        self._missing_warned = set()
        self._load_hlb_values()
        self._load_compatibility_matrices()
        self._load_solubility_values()
        self.continuous_headers = [
            h for h in self.input_headers
            if h not in self.category_headers
        ]
        self.output_headers = [
            "Droplet_Size",
            "PDI",
            "Zeta_P",
            "Phase_Sep",
            "Drug_Loading",
            "Permeability",
        ]
        self.output_dims = len(self.output_headers)
        self.minimize_objective = True
        self.hyper_opt = False
        self.scaling = True
        self.ranges = {
            "Oil_V":          (5.0, 22.5),
            "Surfactant_V":   (10.0, 40.0),
            "Cosurfactant_V": (5.0, 30.0),
            "Sonication":     (0, 3),
        }
        self.oil_v_ranges = {
            "Capmul_MCM":  (5.0, 15.0),
            "Capryol_90":  (5.0, 15.0),
            "Maisine_Oil": (5.0, 10.0),
            "Soybean_Oil": (5.0, 10.0),
        }
        self.surfactant_v_ranges = {
            "Labrasol":  (20, 40),
            "Tween_80":  (20, 40),
            "Tween_20":  (20, 40),
        }
        self.cosurfactant_v_ranges = {
            "Ethanol":           (5, 15),
            "PEG_400":           (5, 20),
            "Propylene_Glycol":  (5, 15),
            "Transcutol_HP":     (10, 20),
        }
        self.fixed_categories = {"API_Name": "Feno"} #Change per campaign
        self.category_values = {
            "Oil":          ["Capmul_MCM", "Capryol_90", "Maisine_Oil", "Oleic_Acid", "Safflower_Oil", "Soybean_Oil"],
            "Surfactant":   ["Kolliphor_RH_40", "Labrasol", "PEG_400", "Pluronic_F-68", "Transcutol_HP", "Tween_20", "Tween_80"],
            "Cosurfactant": ["Cremophor_EL", "Ethanol", "Glycerin", "PEG_400", "Propylene_Glycol", "Transcutol_HP", "Tween_80"],
            "API_Name":     ["A190", "Feno", "blank"],
        }
        self.mesh_categories = {
            "Oil":          ["Capmul_MCM", "Capryol_90", "Maisine_Oil", "Soybean_Oil"],
            "Surfactant":   ["Labrasol", "Tween_20", "Tween_80"],
            "Cosurfactant": ["Ethanol", "PEG_400", "Propylene_Glycol", "Transcutol_HP"],
            "API_Name":     ["A190", "Feno", "blank"],
        }

    def get_dataset(self):
        data = pd.read_csv(self.dataset_path)
        inputs = self._build_input_features(data)
        outputs = data[self.output_headers]
        return inputs, outputs

    def _build_input_features(self, data):
        """Fit ColumnTransformer and assemble [cat | desc | cont] matrix."""
        descriptors = self._add_descriptors(data)

        transformers = []
        if self.category_headers:
            ohe_categories = [self.category_values[h] for h in self.category_headers]
            transformers.append((
                "cat",
                OneHotEncoder(categories=ohe_categories, handle_unknown="ignore"),
                self.category_headers
            ))
        if self.scaling and self.continuous_headers:
            transformers.append((
                "cont",
                FunctionTransformer(self.scale_input, validate=False),
                self.continuous_headers
            ))

        ct = ColumnTransformer(transformers=transformers, remainder="drop")
        processed_inputs = ct.fit_transform(data[self.input_headers])
        if hasattr(processed_inputs, 'toarray'):
            processed_inputs = processed_inputs.toarray()
        self._ct = ct

        n_cat_cols, n_desc_cols = self._get_feature_column_counts()
        cate_part = processed_inputs[:, :n_cat_cols]
        cont_part = processed_inputs[:, n_cat_cols:]
        inputs_with_descriptors = np.hstack([cate_part, descriptors, cont_part])
        self.input_dims = inputs_with_descriptors.shape[1]

        logger.debug("Training data order: [categories, descriptors, continuous]")
        logger.debug("  Categories: columns 0-%d (%d features)", n_cat_cols - 1, n_cat_cols)
        logger.debug(
            "  Descriptors: columns %d-%d (%d features)",
            n_cat_cols, n_cat_cols + n_desc_cols - 1, n_desc_cols
        )
        logger.debug(
            "  Continuous: columns %d-%d (%d features)",
            n_cat_cols + n_desc_cols, inputs_with_descriptors.shape[1] - 1, cont_part.shape[1]
        )
        logger.debug("Final input shape: %s", inputs_with_descriptors.shape)
        logger.debug("  Original features: %d", processed_inputs.shape[1])
        logger.debug("  Descriptor features: %d", n_desc_cols)
        logger.debug("  Total input dimensions: %d", self.input_dims)

        return inputs_with_descriptors

    def _get_feature_column_counts(self) -> tuple:
        """Return (n_cat_cols, n_desc_cols) from the fitted transformer."""
        cat_enc = self._ct.named_transformers_['cat']
        n_cat_cols = sum(len(cats) for cats in cat_enc.categories_)
        n_desc_cols = len(self.descriptor_headers)
        return n_cat_cols, n_desc_cols

    def get_raw_data(self):
        data = pd.read_csv(self.dataset_path)

        return data

    def _load_hlb_values(self):
        """Load HLB values from a CSV file."""
        if not os.path.exists(self.hlb_path):
            raise FileNotFoundError(f"HLB values file not found at {self.hlb_path}")

        df = pd.read_csv(self.hlb_path)

        hlb_dict_raw = {}
        for _, row in df.iterrows():
            hlb_dict_raw[row['Component']] = row['HLB_Value']

        hlb_values = list(hlb_dict_raw.values())
        hlb_min = min(hlb_values)
        hlb_max = max(hlb_values)

        self.hlb_dict = {}
        for component, raw_value in hlb_dict_raw.items():
            normalized_value = (raw_value - hlb_min) / (hlb_max - hlb_min)
            self.hlb_dict[component] = normalized_value

        logger.debug("Loaded %d HLB values", len(self.hlb_dict))
        logger.debug("HLB range: %.1f - %.1f -> normalized to [0, 1]", hlb_min, hlb_max)

    def get_hlb_value(self, component):
        """Get the HLB value for a given component."""
        if component not in self.hlb_dict:
            key = ('hlb', component)
            if key not in self._missing_warned:
                logger.warning("No HLB value for '%s' — defaulting to 0.0", component)
                self._missing_warned.add(key)
            return 0.0
        return self.hlb_dict[component]

    def _load_solubility_values(self):
        """Load solubility values from a CSV file and normalize to [0, 1]."""
        if not os.path.exists(self.solubility_path):
            raise FileNotFoundError(f"Solubility values file not found at {self.solubility_path}")

        df = pd.read_csv(self.solubility_path)

        sol_dict_raw = {}
        for _, row in df.iterrows():
            sol_dict_raw[row['Component']] = row['Solubility_Value']

        sol_values = list(sol_dict_raw.values())
        sol_min = min(sol_values)
        sol_max = max(sol_values)

        self.solubility_dict = {}
        for component, raw_value in sol_dict_raw.items():
            normalized_value = (raw_value - sol_min) / (sol_max - sol_min)
            self.solubility_dict[component] = normalized_value

        logger.debug("Loaded %d solubility values (placeholder data)", len(self.solubility_dict))
        logger.debug("Solubility range: %.3f - %.3f -> normalized to [0, 1]", sol_min, sol_max)

    def get_solubility_value(self, component):
        """Get the normalized solubility value for a given component."""
        if component not in self.solubility_dict:
            key = ('solubility', component)
            if key not in self._missing_warned:
                logger.warning("No solubility value for '%s' — defaulting to 0.0", component)
                self._missing_warned.add(key)
            return 0.0
        return self.solubility_dict[component]

    def _load_compat_matrix(self, path: str) -> dict:
        """Load a CSV compatibility matrix into a nested dict."""
        df = pd.read_csv(path, index_col=0)
        return {row: {col: df.at[row, col] for col in df.columns}
                for row in df.index}

    def _load_compatibility_matrices(self):
        """Load compatibility matrices from CSV files."""
        self.oil_surf_compat = self._load_compat_matrix(self.oil_surf_path)
        self.oil_cosurf_compat = self._load_compat_matrix(self.oil_cosurf_path)
        self.surf_cosurf_compat = self._load_compat_matrix(self.surf_cosurf_path)

        logger.debug("Loaded compatibility matrices:")
        logger.debug(
            "  Oil-Surfactant: %d oils x %d surfactants",
            len(self.oil_surf_compat),
            len(next(iter(self.oil_surf_compat.values())))
        )
        logger.debug(
            "  Oil-Cosurfactant: %d oils x %d cosurfactants",
            len(self.oil_cosurf_compat),
            len(next(iter(self.oil_cosurf_compat.values())))
        )
        logger.debug(
            "  Surfactant-Cosurfactant: %d surfactants x %d cosurfactants",
            len(self.surf_cosurf_compat),
            len(next(iter(self.surf_cosurf_compat.values())))
        )

    def _lookup_compat(self, matrix, row_key, col_key, label):
        """Lookup a compatibility value, warning and returning 0 for missing or NaN entries."""
        raw = matrix.get(row_key, {}).get(col_key)
        if raw is None or (isinstance(raw, float) and pd.isna(raw)):
            key = (label, row_key, col_key)
            if key not in self._missing_warned:
                logger.warning("No %s compat entry for ('%s', '%s') — defaulting to 0", label, row_key, col_key)
                self._missing_warned.add(key)
            return 0
        return int(raw)

    def get_compatibility_score(self, oil, surfactant, cosurfactant):
        """Get compatibility score for the given components."""
        oil_surf_score = self._lookup_compat(self.oil_surf_compat, oil, surfactant, "oil-surfactant")
        oil_cosurf_score = self._lookup_compat(self.oil_cosurf_compat, oil, cosurfactant, "oil-cosurfactant")
        surf_cosurf_score = self._lookup_compat(self.surf_cosurf_compat, surfactant, cosurfactant, "surfactant-cosurfactant")
        return oil_surf_score, oil_cosurf_score, surf_cosurf_score

    def get_descriptor_row(self, row):
        """Return descriptor values for one categorical combination row.

        Args:
            row: DataFrame row with columns matching category_headers.

        Returns:
            List of descriptor floats for this combination.
        """
        oil = row['Oil']
        surf = row['Surfactant']
        cosurf = row['Cosurfactant']

        hlb_oil = self.get_hlb_value(oil)
        hlb_surf = self.get_hlb_value(surf)
        hlb_cosurf = self.get_hlb_value(cosurf)

        oil_surf, oil_cosurf, surf_cosurf = (
            self.get_compatibility_score(oil, surf, cosurf)
        )

        sol_oil = self.get_solubility_value(oil)
        sol_surf = self.get_solubility_value(surf)
        sol_cosurf = self.get_solubility_value(cosurf)

        return [
            hlb_oil, hlb_surf, hlb_cosurf,
            oil_surf, oil_cosurf, surf_cosurf,
            sol_oil, sol_surf, sol_cosurf,
        ]

    def _add_descriptors(self, data):
        """Compute descriptor matrix by delegating each row to get_descriptor_row."""
        logger.debug("Adding descriptors for %d data points...", len(data))

        descriptors = np.array([self.get_descriptor_row(row) for _, row in data.iterrows()])

        if not np.all((descriptors >= 0) & (descriptors <= 1)):
            logger.warning("Descriptor values are not in the expected range [0, 1].")
            logger.warning(" Min values: %s", descriptors.min(axis=0))
            logger.warning(" Max values: %s", descriptors.max(axis=0))
            logger.warning(" Descriptor headers: %s", self.descriptor_headers)
        else:
            logger.debug("All descriptor values are within the expected range [0, 1].")

        logger.debug("Generated %d descriptor columns: %s", descriptors.shape[1], self.descriptor_headers)

        return descriptors

    def get_input_dims(self):
        return self.input_dims

    def get_output_dims(self):
        return self.output_dims

    def objective_function(self, preds, args=None):
        """Minimization objective over the 6 surrogate outputs.

        Additive scalar objective. The stable-side ``formulation_loss`` is a
        weighted sum over five component scores; Phase_Sep contributes an
        additive penalty ``PHASE_SEP_WEIGHT * clip(sep, 0, 1)``. The current
        ``PHASE_SEP_WEIGHT`` is a function-local constant (see body); tune
        there. At weight 50, a 30%-predicted-instability candidate adds 15 to
        the objective — comparable in magnitude to a single heavily-weighted
        stable-side miss, so Phase_Sep matters but does not dominate.

        Score components:
          * Size: one-sided penalty above 100 nm, slope 1/900.
          * PDI: penalty above 0.1 (slope 1/0.9); gentle bonus below 0.1
            (slope 1/(0.9*5), 1/5 of the penalty side).
          * Zeta: penalty for |zeta| > 10, slope 1/10.
          * Drug_Loading: V-shape around 100% with a forgiving dead-zone
            inside [95, 105] (inner slope 1/130) and a 5x-steeper outer slope
            (1/26). NaN contributes 0. No bonus side.
          * Permeability: penalty below 20e-6 (slope 1/20e-6); gentle bonus
            above (slope 1/(20e-6*5), 1/5 of the penalty side). NaN
            contributes 0.

        Weights: Size 3x, PDI 2x, Zeta 1x, Drug_Loading 2x, Permeability 3x.

        The objective is NOT guaranteed non-negative: PDI and Permeability
        bonuses can drive ``formulation_loss`` slightly below zero for ideal
        candidates. The additive Phase_Sep term is always >= 0.

        Args:
            preds: shape (n_samples, 6) — columns follow ``output_headers``
                   order: [Droplet_Size, PDI, Zeta_P, Phase_Sep,
                           Drug_Loading, Permeability].
            args:  unused; retained for interface compatibility.

        Returns:
            shape (n_samples,) scalar objective. Lower is better.
        """
        size = preds[:, 0]
        pdi  = preds[:, 1]
        zeta = preds[:, 2]
        sep  = preds[:, 3]
        dl   = preds[:, 4]
        perm = preds[:, 5]

        PHASE_SEP_WEIGHT = 50

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
        sep_clipped = np.clip(sep, 0.0, 1.0)
        return formulation_loss + (sep_clipped * PHASE_SEP_WEIGHT)

    def get_worst_case_output(self) -> np.ndarray:
        """Return a fabricated worst-case output for hallucinated batch selection.

        Represents a fully phase-separated formulation with zero drug performance.
        Using explicit 0.0 for Drug_Loading and Permeability (rather than NaN)
        ensures Phase 2 regressors for those targets also learn to avoid the
        selected region, not just the physical property models.

        Returns:
            shape (6,) array: [Droplet_Size, PDI, Zeta_P, Phase_Sep,
                Drug_Loading, Permeability]
        """
        return np.array([10000.0, 1.0, 100.0, 1.0, 0.0, 0.0])

    def scale_input(self, arr):
        mins = np.array([self.ranges[h][0] for h in self.continuous_headers])
        maxs = np.array([self.ranges[h][1] for h in self.continuous_headers])
        return (arr - mins) / (maxs - mins)

    def unscale_input(self, encoded):
        n_cat_cols, n_desc_cols = self._get_feature_column_counts()
        cat_enc = self._ct.named_transformers_['cat']

        cat_part = encoded[:n_cat_cols]
        cont_part = encoded[n_cat_cols + n_desc_cols:]

        cat_vals = cat_enc.inverse_transform(cat_part.reshape(1, -1))[0]

        unscaled_cont = []
        for val_scaled, header in zip(cont_part, self.continuous_headers):
            minv, maxv = self.ranges[header]
            unscaled_cont.append(val_scaled * (maxv - minv) + minv)

        result = []
        for h in self.input_headers:
            if h in self.continuous_headers:
                idx = self.continuous_headers.index(h)
                result.append(unscaled_cont[idx])
            else:
                idx = self.category_headers.index(h)
                result.append(cat_vals[idx])

        return result


def get_app_class(class_name):
    app_classes = {
        "microemulsion": MicroemulsionFormulation(),
    }
    return app_classes.get(class_name, "Key not found")
