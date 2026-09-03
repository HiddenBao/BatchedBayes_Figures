from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

from BayesianOptimization.mesh_utils import (
    build_coarse_mesh,
    build_fine_mesh_per_winner,
    compute_acquisition,
    eval_surrogate,
    select_top_categories,
)
from BayesianOptimization.qmc import generate_qmc_normal
from BayesianOptimization.surrogate_models.get_surrogate import (
    get_surrogate_model,
)
from BayesianOptimization.surrogate_models.simple_gp import (
    _GPR_IDXS,
    _PHASE_SEP_IDX,
)


class BatchResult:
    """Container for batch selection results."""

    def __init__(
            self,
            selected_inputs: np.ndarray,
            acquisition_values: np.ndarray,
            indices: list[int] | None = None,
            total_candidates: int | None = None,
            method_used: str | None = None,
    ) -> None:
        """Initialize batch results.

        Args:
            selected_inputs: Array of selected input points.
            acquisition_values: Acquisition values for selected points.
            indices: Optional indices of selected points in the candidate pool.
            total_candidates: Total number of candidates considered.
            method_used: Name of the batch selection method.
        """
        self.selected_inputs = selected_inputs
        self.acquisition_values = acquisition_values
        self.indices = indices
        self.total_candidates = total_candidates
        self.method_used = method_used

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"BatchResult(batch_size={len(self.selected_inputs)}, "
            f"method={self.method_used}, "
            f"total_candidates={self.total_candidates})"
        )

    def __len__(self) -> int:
        """Return batch size."""
        return len(self.selected_inputs)

    @property
    def coordinates(self) -> np.ndarray:
        """Alias for selected_inputs."""
        return self.selected_inputs


class BatchSelector:
    """Base class for all batch selection strategies."""

    def select_batch(
            self,
            fine_inputs: np.ndarray,
            acq_fine: np.ndarray,
            model: Any,
            args: Any,
            application: Any,
            **context: Any,
    ) -> BatchResult:
        """Select a batch of points for evaluation.

        Args:
            fine_inputs: Candidate input points from the fine mesh.
            acq_fine: Acquisition values for the fine mesh candidates.
            model: Trained surrogate model.
            args: Experiment configuration namespace.
            application: Application object defining the optimization problem.
            **context: Additional context passed by the pipeline.

        Returns:
            BatchResult containing selected inputs and acquisition
            values; subclasses define the concrete return value.

        Raises:
            NotImplementedError: Always; subclasses must implement this.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is not implemented."
        )


class HallucinatedBatchSelector(BatchSelector):
    """Hallucinated batch selection - full re-evaluation of the meshes."""

    def __init__(
            self,
            n_duplicates: int = 3,
    ) -> None:
        """Initialize hallucinated selector.

        Args:
            n_duplicates: Number of times to repeat the hallucinated point.
        """
        self.n_duplicates = n_duplicates

    def select_batch(
            self,
            fine_inputs: np.ndarray,
            acq_fine: np.ndarray,
            model: Any,
            args: Any,
            application: Any,
            **context: Any,
    ) -> BatchResult:
        """Select a batch using hallucinated selection.

        Args:
            fine_inputs: Candidate input points from the fine mesh.
            acq_fine: Acquisition values for the fine mesh candidates.
            model: Trained surrogate model.
            args: Experiment configuration namespace.
            application: Application object defining the optimization problem.
            **context: Pipeline context including categories, rng, etc.

        Returns:
            BatchResult with hallucinated-selected points and acq values.
        """
        context['fine_inputs'] = fine_inputs
        required_context = self._extract_context(context)

        selected_inputs_list = self._hallucinated_algorithm(
            model, args, application, required_context
        )

        selected_inputs = np.array(selected_inputs_list)

        selected_acq_values = self._compute_acquisition_for_inputs(
            selected_inputs, model, args, application, required_context
        )

        return BatchResult(
            selected_inputs=selected_inputs,
            acquisition_values=selected_acq_values,
            indices=None,
            total_candidates=len(fine_inputs),
            method_used="hallucinated",
        )

    def _get_lie_value(
            self,
            application: Any,
    ) -> np.ndarray:
        """Return the fabricated worst-case output for hallucination.

        Args:
            application: Application with get_worst_case_output method.

        Returns:
            A 1-D worst-case output vector to use as the hallucinated label.
        """
        return application.get_worst_case_output()

    def _eval_acquisition(
            self,
            mesh: np.ndarray,
            model: Any,
            args: Any,
            application: Any,
            context: dict[str, Any],
    ) -> np.ndarray:
        """Evaluate acquisition function over a mesh of candidates.

        Calls eval_surrogate, optionally generates QMC samples when
        args.need_qmc is True, then calls compute_acquisition.

        Args:
            mesh: Candidate input points, shape (n_candidates, d).
            model: Trained surrogate model.
            args: Experiment configuration namespace. Must have need_qmc,
                qmc_samples, output_dimensions, and minimize_objective.
            application: Application object defining the optimization
                problem.
            context: Pipeline context dict. Must contain
                'choice_function', 'current_best', and 'rng'.

        Returns:
            Acquisition values array of shape (n_candidates,).
        """
        mu, sigma = eval_surrogate(model, mesh)

        qmc = None
        if args.need_qmc:
            qmc = generate_qmc_normal(
                args.qmc_samples, args.output_dimensions, context['rng']
            )
            logger.debug(
                "QMC shape: %s, expected: (%d, %d)",
                qmc.shape, args.qmc_samples, args.output_dimensions,
            )

        return compute_acquisition(
            context['choice_function'], mesh, mu, sigma,
            context['current_best'], args, context['rng'], application, qmc,
        )

    def _compute_acquisition_for_inputs(
            self,
            inputs: np.ndarray,
            model: Any,
            args: Any,
            application: Any,
            context: dict[str, Any],
    ) -> np.ndarray:
        """Compute acquisition values for selected inputs.

        Args:
            inputs: Input points to evaluate.
            model: Trained surrogate model.
            args: Experiment configuration namespace.
            application: Application object.
            context: Pipeline context dictionary.

        Returns:
            Acquisition values for each input point.
        """
        return self._eval_acquisition(inputs, model, args, application, context)

    def _extract_context(
            self, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract required parameters from context.

        Args:
            context: Raw context dictionary from the pipeline.

        Returns:
            Filtered context containing only required and optional keys.

        Raises:
            ValueError: If any required key is missing from context.
        """
        required_keys = [
            'categories', 'x_train', 'choice_function',
            'current_best', 'rng', 'd_cont', 'fine_inputs',
        ]

        missing_keys = [key for key in required_keys if key not in context]
        if missing_keys:
            raise ValueError(f"Missing required context: {missing_keys}.")

        return {
            key: context[key]
            for key in required_keys + ['combos']
            if key in context
        }

    def _remove_duplicates(
            self,
            current_fine_mesh: np.ndarray,
            already_selected: list[np.ndarray],
    ) -> np.ndarray:
        """Remove points that have already been selected.

        Args:
            current_fine_mesh: Candidate points array to filter.
            already_selected: List of previously selected point arrays.

        Returns:
            Filtered mesh with duplicate points removed.
        """
        if len(already_selected) == 0:
            return current_fine_mesh

        tolerance = 1e-8
        selected_tuples = {
            tuple(np.round(point / tolerance) * tolerance)
            for point in already_selected
        }

        mask = [
            tuple(np.round(point / tolerance) * tolerance)
            not in selected_tuples
            for point in current_fine_mesh
        ]

        return current_fine_mesh[np.array(mask)]

    def _select_best_point(
            self,
            fine_mesh: np.ndarray,
            model: Any,
            args: Any,
            application: Any,
            context: dict[str, Any],
    ) -> np.ndarray:
        """Select the best point from the fine mesh via acquisition function.

        Args:
            fine_mesh: Candidate input points.
            model: Trained surrogate model.
            args: Experiment configuration namespace.
            application: Application object.
            context: Pipeline context dictionary.

        Returns:
            The best candidate point as a 1-D array.
        """
        acq_fine = self._eval_acquisition(
            fine_mesh, model, args, application, context
        )

        best_idx = int(np.nanargmax(acq_fine))

        return fine_mesh[best_idx]

    def _update_model_with_hallucination(
            self,
            model: Any,
            augmented_inputs: np.ndarray,
            augmented_outputs: np.ndarray,
            args: Any,
            application: Any,
            rng: np.random.Generator,
    ) -> Any:
        """Retrain the surrogate on the augmented dataset.

        Args:
            model: Current surrogate model (returned as fallback on failure).
            augmented_inputs: Training inputs including hallucinated points.
            augmented_outputs: Training outputs including hallucinated labels.
            args: Experiment configuration namespace.
            application: Application object.
            rng: Random number generator.

        Returns:
            Newly retrained surrogate model, or original model if failed.
        """
        try:
            new_model = get_surrogate_model(args, rng, application)
            new_model.fit(augmented_inputs, augmented_outputs)
            return new_model

        except Exception as e:
            logger.warning("Model retraining failed: %s", e)
            return model

    def _build_next_fine_mesh(
            self,
            batch_idx: int,
            current_model: Any,
            args: Any,
            application: Any,
            context: dict[str, Any],
    ) -> np.ndarray:
        """Rebuild the fine mesh for batch iteration batch_idx > 0.

        Runs a coarse-mesh pass with the current (possibly hallucinated)
        model, selects the top-K categories, then generates a fresh fine
        mesh for those categories.

        Args:
            batch_idx: Current batch iteration index (must be > 0).
            current_model: Surrogate model (possibly retrained with
                hallucinated data).
            args: Experiment configuration namespace.
            application: Application object.
            context: Pipeline context dict containing 'categories',
                'd_cont', and 'x_train'.

        Returns:
            Fine mesh array of shape (n_fine, d_cat + d_cont).
        """
        coarse_input, cat_idx, cont_pts = build_coarse_mesh(
            context['categories'], args,
            context['d_cont'], application,
            combos=context.get('combos'),
        )

        acq_coarse = self._eval_acquisition(
            coarse_input, current_model, args, application, context,
        )

        winners = select_top_categories(
            acq_coarse,
            cat_indices=cat_idx,
            cont_points=cont_pts,
            top_k=args.top_k_categories,
        )
        logger.info(
            "Updated top categories for point %d: %s.",
            batch_idx + 1, [w[0] for w in winners],
        )

        current_fine_mesh = build_fine_mesh_per_winner(
            winners, context['categories'], args,
            context['x_train'], application,
            combos=context.get('combos'),
        )
        logger.info(
            "Generated fine mesh with %d candidates.",
            len(current_fine_mesh),
        )

        return current_fine_mesh

    def _augment_training_data(
            self,
            accumulated_inputs: np.ndarray,
            accumulated_outputs: np.ndarray,
            best_input: np.ndarray,
            application: Any,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Augment the accumulated training data with a hallucinated point.

        The best_input is repeated n_duplicates times with the worst-case
        fabricated output from application.get_worst_case_output().

        Args:
            accumulated_inputs: Current accumulated input array,
                shape (n_train, d).
            accumulated_outputs: Current accumulated output array,
                shape (n_train, n_outputs).
            best_input: The selected point for this batch slot,
                shape (d,).
            application: Application object with get_worst_case_output.

        Returns:
            Tuple of (new_accumulated_inputs, new_accumulated_outputs)
            with hallucinated rows appended.
        """
        hallucinated_output = self._get_lie_value(application).reshape(1, -1)
        dup_in = np.repeat(
            best_input.reshape(1, -1), self.n_duplicates, axis=0,
        )
        dup_out = np.repeat(
            hallucinated_output, self.n_duplicates, axis=0,
        )
        new_inputs = np.vstack([accumulated_inputs, dup_in])
        new_outputs = np.vstack([accumulated_outputs, dup_out])

        logger.debug(
            "Added %d hallucinated copies to training data.",
            self.n_duplicates,
        )

        return new_inputs, new_outputs

    def _hallucinated_algorithm(
            self,
            model: Any,
            args: Any,
            application: Any,
            context: dict[str, Any],
    ) -> list[np.ndarray]:
        """Run the main hallucinated batch selection algorithm.

        Args:
            model: Initial surrogate model.
            args: Experiment configuration namespace.
            application: Application with dataset and objective function.
            context: Pipeline context dictionary.

        Returns:
            List of selected input point arrays, one per batch slot.
        """
        selected_inputs_list: list[np.ndarray] = []
        current_model = model

        original_inputs, original_outputs = map(
            np.asarray, application.get_dataset(),
        )
        accumulated_inputs = original_inputs.copy()
        accumulated_outputs = original_outputs.copy()

        for batch_idx in range(args.batch_size):
            logger.info(
                "Selecting batch point %d/%d.",
                batch_idx + 1, args.batch_size,
            )

            if batch_idx == 0:
                current_fine_mesh = context['fine_inputs']
                if current_fine_mesh is None:
                    raise ValueError(
                        "fine_inputs not provided in context "
                        "for first iteration."
                    )
                logger.debug("Using pre-computed fine mesh for first point.")
            else:
                current_fine_mesh = self._build_next_fine_mesh(
                    batch_idx, current_model, args, application, context,
                )

            current_fine_mesh = self._remove_duplicates(
                current_fine_mesh, selected_inputs_list,
            )

            if len(current_fine_mesh) == 0:
                logger.warning(
                    "No new candidates for batch point %d; stopping early.",
                    batch_idx + 1,
                )
                break

            best_input = self._select_best_point(
                current_fine_mesh, current_model, args, application, context,
            )
            selected_inputs_list.append(best_input)
            logger.info("Selected point %d: %s.", batch_idx + 1, best_input)

            if batch_idx < args.batch_size - 1:
                accumulated_inputs, accumulated_outputs = (
                    self._augment_training_data(
                        accumulated_inputs, accumulated_outputs,
                        best_input, application,
                    )
                )
                current_model = self._update_model_with_hallucination(
                    current_model, accumulated_inputs, accumulated_outputs,
                    args, application, context['rng'],
                )
                logger.info(
                    "Model retrained with hallucinated data for point %d.",
                    batch_idx + 1,
                )

        return selected_inputs_list


class ThompsonBatchSelector(BatchSelector):
    """Parallel Thompson Sampling batch selection.

    Draws B coherent posterior function samples from the fitted GPs,
    passes each through the application's objective function, and
    selects the argmin of each as a batch point. No model retraining,
    no fake observations.

    Uses gpr.predict(X, return_cov=True) for posterior covariance
    (not the prior kernel), and Cholesky factorization for coherent
    spatial sampling. Phase_Sep is sampled independently using
    Bernoulli-variance noise on the GPC probability.
    """

    # GPR index -> output column mapping (imported from simple_gp)
    _GPR_COL_MAP = _GPR_IDXS

    def select_batch(
            self,
            fine_inputs: np.ndarray,
            acq_fine: np.ndarray,
            model: Any,
            args: Any,
            application: Any,
            **context: Any,
    ) -> BatchResult:
        """Select a batch using parallel Thompson Sampling.

        Args:
            fine_inputs: Candidate input points from the fine mesh.
            acq_fine: Acquisition values (unused by pTS; accepted for
                interface compatibility).
            model: Trained SimpleGPModel with _gprs and _gpc_p_sep.
            args: Experiment configuration; must have batch_size.
            application: Application with objective_function method.
            **context: Must contain 'rng' (numpy random Generator).

        Returns:
            BatchResult with selected points and sample objective values.
        """
        rng = context['rng']
        n_candidates = len(fine_inputs)
        batch_size = min(args.batch_size, n_candidates)

        if batch_size < args.batch_size:
            logger.warning(
                "Only %d candidates available for batch of %d; "
                "returning all candidates.",
                n_candidates, args.batch_size,
            )

        # Pre-compute posterior means, stds, and Cholesky factors
        mu = model.predict(fine_inputs)
        sigma = model.predict_std(fine_inputs)
        cholesky_factors = self._compute_cholesky_factors(
            model, fine_inputs, n_candidates,
        )

        # Pre-compute Phase_Sep marginal sampling params
        p_sep = model._gpc_p_sep(fine_inputs)
        sigma_sep = np.sqrt(p_sep * (1.0 - p_sep))

        # Precompute category IDs for max_per_category enforcement
        max_per_category = getattr(args, 'max_per_category', 0)
        d_cont = context.get('d_cont', 3)
        if max_per_category > 0:
            _, cat_ids = np.unique(
                fine_inputs[:, :-d_cont], axis=0, return_inverse=True,
            )
            logger.debug(
                "max_per_category=%d: %d unique categories in fine mesh.",
                max_per_category, len(np.unique(cat_ids)),
            )
        else:
            cat_ids = None

        # Draw B posterior samples and select argmin of each
        selected_indices: list[int] = []
        sample_objectives: list[float] = []
        category_counts: dict[int, int] = {}

        for b in range(batch_size):
            samples_b = self._draw_coherent_sample(
                mu, cholesky_factors, sigma, p_sep, sigma_sep,
                n_candidates, rng,
            )
            idx, obj_val = self._select_point_from_sample(
                samples_b, application, args, selected_indices,
                cat_ids, category_counts, max_per_category,
            )
            selected_indices.append(idx)
            sample_objectives.append(obj_val)
            if max_per_category > 0 and cat_ids is not None:
                cat_id = int(cat_ids[idx])
                category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
            logger.info(
                "Thompson sample %d/%d: selected index %d, "
                "sample objective=%.6f",
                b + 1, batch_size, idx, obj_val,
            )

        selected_inputs = fine_inputs[selected_indices]

        return BatchResult(
            selected_inputs=selected_inputs,
            acquisition_values=np.array(sample_objectives),
            indices=selected_indices,
            total_candidates=n_candidates,
            method_used="thompson",
        )

    def _compute_cholesky_factors(
            self,
            model: Any,
            X: np.ndarray,
            n: int,
    ) -> list[np.ndarray | None]:
        """Compute Cholesky factors of posterior covariance for each GPR.

        Args:
            model: Fitted SimpleGPModel.
            X: Candidate points, shape (n, d).
            n: Number of candidates.

        Returns:
            List of Cholesky factors (one per GPR). Entry is None if
            Cholesky failed and independent sampling should be used.
        """
        factors: list[np.ndarray | None] = []

        for gpr_idx, col in enumerate(self._GPR_COL_MAP):
            gpr = model._gprs[gpr_idx]
            try:
                _, cov = gpr.predict(X, return_cov=True)
                L = self._safe_cholesky(cov, n)
                factors.append(L)
                logger.debug(
                    "Cholesky OK for GPR[%d] (col %d).", gpr_idx, col,
                )
            except np.linalg.LinAlgError:
                logger.warning(
                    "Cholesky failed for GPR[%d] (col %d); "
                    "falling back to independent sampling.",
                    gpr_idx, col,
                )
                factors.append(None)

        return factors

    @staticmethod
    def _safe_cholesky(
            cov: np.ndarray,
            n: int,
    ) -> np.ndarray:
        """Cholesky with progressive jitter on failure.

        Args:
            cov: Posterior covariance matrix, shape (n, n).
            n: Matrix dimension.

        Returns:
            Lower-triangular Cholesky factor L.

        Raises:
            np.linalg.LinAlgError: If Cholesky fails at all jitter levels.
        """
        for jitter in (0.0, 1e-6, 1e-5, 1e-4):
            try:
                return np.linalg.cholesky(cov + jitter * np.eye(n))
            except np.linalg.LinAlgError:
                continue
        raise np.linalg.LinAlgError(
            "Cholesky failed at all jitter levels."
        )

    def _draw_coherent_sample(
            self,
            mu: np.ndarray,
            cholesky_factors: list[np.ndarray | None],
            sigma: np.ndarray,
            p_sep: np.ndarray,
            sigma_sep: np.ndarray,
            n: int,
            rng: np.random.Generator,
    ) -> np.ndarray:
        """Draw one coherent 6-output posterior sample across all candidates.

        Args:
            mu: Mean predictions, shape (n, 6) in original space.
            cholesky_factors: Cholesky factors per GPR (None = independent).
            sigma: Std predictions, shape (n, 6) for independent fallback.
            p_sep: GPC phase separation probability, shape (n,).
            sigma_sep: Bernoulli std sqrt(p*(1-p)), shape (n,).
            n: Number of candidates.
            rng: Random number generator.

        Returns:
            Sampled predictions, shape (n, 6).
        """
        samples = np.copy(mu)

        # GPR targets: coherent or independent sampling
        for gpr_idx, col in enumerate(self._GPR_COL_MAP):
            z = rng.standard_normal(n)
            L = cholesky_factors[gpr_idx]
            if L is not None:
                # Coherent: mu + L @ z (both in original space)
                samples[:, col] = mu[:, col] + L @ z
            else:
                # Fallback: independent marginal sampling
                samples[:, col] = mu[:, col] + sigma[:, col] * z

        # Phase_Sep: independent marginal perturbation (Option B)
        z_sep = rng.standard_normal(n)
        samples[:, _PHASE_SEP_IDX] = np.clip(
            p_sep + sigma_sep * z_sep, 0.0, 1.0,
        )

        return samples

    @staticmethod
    def _select_point_from_sample(
            samples: np.ndarray,
            application: Any,
            args: Any,
            already_selected: list[int],
            cat_ids: np.ndarray | None = None,
            category_counts: dict[int, int] | None = None,
            max_per_category: int = 0,
    ) -> tuple[int, float]:
        """Select the best point from a posterior sample.

        Args:
            samples: Sampled predictions, shape (n, 6).
            application: Application with objective_function.
            args: Experiment configuration.
            already_selected: Indices already chosen in this batch.
            cat_ids: Integer category ID per candidate, shape (n,). None
                disables category enforcement.
            category_counts: Current count of selections per category ID.
            max_per_category: Maximum allowed selections per category.
                0 disables enforcement.

        Returns:
            Tuple of (selected_index, objective_value).
        """
        obj = application.objective_function(samples, args)
        masked_obj = obj.copy()

        # Mask already-selected indices
        for idx in already_selected:
            masked_obj[idx] = np.inf

        # Mask candidates from exhausted categories
        if max_per_category > 0 and cat_ids is not None and category_counts:
            exhausted = {
                cid for cid, cnt in category_counts.items()
                if cnt >= max_per_category
            }
            if exhausted:
                masked_obj[np.isin(cat_ids, list(exhausted))] = np.inf

        # If all candidates are exhausted (batch_size > n_cats * max_per_category),
        # fall back gracefully: ignore category constraint for this slot
        if np.all(masked_obj == np.inf):
            logger.warning(
                "All categories exhausted by max_per_category=%d; "
                "ignoring category constraint for this slot.",
                max_per_category,
            )
            masked_obj = obj.copy()
            for idx in already_selected:
                masked_obj[idx] = np.inf

        best_idx = int(np.argmin(masked_obj))
        return best_idx, obj[best_idx]


class GreedyEIScreeningBatchSelector(BatchSelector):
    """EI-greedy batch selection with categorical diversity enforcement.

    Selects the highest-EI point(s) per unique categorical combo from
    the pre-computed fine mesh, then takes the top batch_size points
    by EI across all categories. Requires no model retraining or
    posterior sampling.

    max_per_category controls how many points may be taken from each
    categorical combo. 0 is treated as 1 (minimum diversity guarantee).
    """

    def select_batch(
            self,
            fine_inputs: np.ndarray,
            acq_fine: np.ndarray,
            model: Any,
            args: Any,
            application: Any,
            **context: Any,
    ) -> BatchResult:
        """Select a batch using EI-greedy categorical screening.

        Args:
            fine_inputs: Candidate input points from the fine mesh,
                shape (n_fine, d).
            acq_fine: Pre-computed acquisition values, shape (n_fine,).
                Higher values are better (maximisation convention).
            model: Trained surrogate model (unused; accepted for
                interface compatibility).
            args: Experiment configuration namespace. Must have
                batch_size, max_per_category, and top_k_categories.
            application: Application object (unused; accepted for
                interface compatibility).
            **context: Must contain 'd_cont' (int): number of
                continuous input dimensions.

        Returns:
            BatchResult with selected points sorted descending by EI,
            capped at batch_size.
        """
        d_cont: int = context['d_cont']
        max_per_category: int = getattr(args, 'max_per_category', 0)
        effective_max: int = 1 if max_per_category == 0 else max_per_category

        top_k = getattr(args, 'top_k_categories', None)
        if (
            effective_max == 1
            and top_k is not None
            and top_k < args.batch_size
        ):
            logger.warning(
                "top_k_categories (%d) < batch_size (%d) with "
                "max_per_category=1; batch may be smaller than requested.",
                top_k, args.batch_size,
            )

        _, cat_ids = np.unique(
            fine_inputs[:, :-d_cont], axis=0, return_inverse=True,
        )

        winner_inputs: list[np.ndarray] = []
        winner_acqs: list[np.ndarray] = []

        for cat_id in np.unique(cat_ids):
            mask = cat_ids == cat_id
            group_acq = acq_fine[mask]
            group_inputs = fine_inputs[mask]
            top_n = min(effective_max, len(group_acq))
            top_local_idxs = np.argsort(group_acq)[::-1][:top_n]
            winner_inputs.append(group_inputs[top_local_idxs])
            winner_acqs.append(group_acq[top_local_idxs])

        all_inputs = np.vstack(winner_inputs)
        all_acq = np.concatenate(winner_acqs)
        order = np.argsort(all_acq)[::-1][: args.batch_size]

        logger.info(
            "Greedy EI screening selected %d/%d points from %d categories.",
            len(order), args.batch_size, len(np.unique(cat_ids)),
        )

        return BatchResult(
            selected_inputs=all_inputs[order],
            acquisition_values=all_acq[order],
            indices=None,
            total_candidates=len(fine_inputs),
            method_used="greedy_ei_screening",
        )


def get_batch_selector(method: str, **kwargs: Any) -> BatchSelector:
    """Factory function to get the appropriate batch selector.

    Args:
        method: Batch selection method name.
        **kwargs: Additional keyword arguments forwarded to the selector.

    Returns:
        A BatchSelector instance.

    Raises:
        ValueError: If the method name is not recognized.
    """
    if method == "hallucinated":
        return HallucinatedBatchSelector()

    if method == "thompson":
        return ThompsonBatchSelector()

    if method == "greedy_ei_screening":
        return GreedyEIScreeningBatchSelector()

    raise ValueError(
        f"Unknown batch method: '{method}'. "
        f"Available methods: hallucinated, thompson, greedy_ei_screening"
    )
