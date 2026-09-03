from scipy.stats import qmc, norm
import numpy as np


def generate_qmc_normal(n, d, random_generator):
    """
    Generate n d-dimensional samples using the QMC sequence. For one datapoint at a time.
    """

    sampler = qmc.Sobol(
        d,
        bits = 30,
        seed = random_generator,
        scramble = True
    )
    sampler = qmc.MultivariateNormalQMC(
        mean = np.zeros(d),
        engine = sampler
    )
    normal_samples = sampler.random(n)  # shape (n, d)

    return normal_samples  # shape (n, d)

# def generate_qmc_samples(preds, stds, n, d, random_generator):
#     normal_samples = generate_qmc_normal(n, d, random_generator) # z scores shape (n, d)
#     samples = normal_samples * stds + preds # shape (n, d)
#     return samples
