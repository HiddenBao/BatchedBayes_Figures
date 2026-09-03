from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def verify_dimensions_simple(x_train, coarse_input, fine_input):
    """Simple dimension check to make sure everything matches."""

    logger.debug(
        "Dimension check — train: %s, coarse: %s, fine: %s",
        x_train.shape, coarse_input.shape, fine_input.shape,
    )

    all_same = (x_train.shape[1] == coarse_input.shape[1] == fine_input.shape[1])

    if all_same:
        logger.debug("All feature dimensions match: %d", x_train.shape[1])
        return True
    else:
        logger.warning(
            "Dimension mismatch — train=%d, coarse=%d, fine=%d",
            x_train.shape[1], coarse_input.shape[1], fine_input.shape[1],
        )
        return False
