"""Surrogate model factory."""
from typing import Any

from BayesianOptimization.surrogate_models.updated_surrogate import SimpleGPModel


def get_surrogate_model(
    args: Any,
    random_generator: Any,
    application: Any,
) -> SimpleGPModel:
    """Return a SimpleGPModel for the given args and application.

    Args:
        args: CLI argument namespace.
        random_generator: NumPy random generator.
        application: Application object.

    Returns:
        SimpleGPModel instance.
    """
    return SimpleGPModel(
        application=application,
        args=args,
        random_generator=random_generator,
    )
