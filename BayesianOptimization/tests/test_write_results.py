"""Tests for API-aware output filename in write_results."""
from __future__ import annotations

import types

import numpy as np

from BayesianOptimization.linear import write_results


class _StubApp:
    """Minimal application stand-in for write_results."""

    def __init__(self, api_name: str | None):
        self.fixed_categories = {"API_Name": api_name} if api_name else {}
        self.input_headers = ["a", "b"]
        self.output_headers = ["y"]

    def objective_function(self, output, args):
        # output shape (1, 1) — return shape (1,)
        return np.asarray([float(output[0, 0])])

    def unscale_input(self, point):
        return list(point)


class _StubModel:
    def predict(self, x):
        # x shape (1, d) — return shape (1, 1)
        return np.asarray([[1.23]])


def test_write_results_uses_api_specific_filename(tmp_path):
    """When fixed_categories has an API_Name, the filename includes it."""
    app = _StubApp(api_name="A190")
    model = _StubModel()
    selected = np.array([[0.5, 0.5]])
    args = types.SimpleNamespace(output_dir=str(tmp_path))

    write_results(selected, model, app, args)

    expected = tmp_path / "results_linear_A190.csv"
    assert expected.exists(), (
        f"Expected {expected}, but got these files: "
        f"{list(tmp_path.iterdir())}"
    )


def test_write_results_falls_back_when_no_api(tmp_path):
    """When fixed_categories is empty, filename uses the 'all' suffix."""
    app = _StubApp(api_name=None)
    model = _StubModel()
    selected = np.array([[0.5, 0.5]])
    args = types.SimpleNamespace(output_dir=str(tmp_path))

    write_results(selected, model, app, args)

    expected = tmp_path / "results_linear_all.csv"
    assert expected.exists(), (
        f"Expected {expected}, but got these files: "
        f"{list(tmp_path.iterdir())}"
    )
