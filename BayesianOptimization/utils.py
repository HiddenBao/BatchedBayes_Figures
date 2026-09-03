"""Contains utility functions for the project. This file should not contain imports from other project files.
May include things like loading and saving data, or other general purpose functions."""

import csv
import os

import numpy as np


def round_inputs(inputs, mesh_size):
    """
    Round inputs to the nearest mesh point.
    """

    rounded_inputs = np.round(inputs * (mesh_size - 1)) / (mesh_size - 1)

    return rounded_inputs


def get_inputs_grid(mesh_size, input_dimensions):
    """
    Get a grid of input values to evaluate the process model on.
    """

    inputs = np.meshgrid(*[np.linspace(0, 1, mesh_size) for _ in range(input_dimensions)])
    inputs = np.stack(inputs, axis = -1).reshape(-1, input_dimensions)

    return inputs


def get_fine_mesh_around_point(
        point,
        mesh_size,
        fine_mesh_size,
        input_dimensions,
        training_inputs = None
):
    """
    Get a fine mesh around a point.
    """

    fine_mesh = get_inputs_grid(fine_mesh_size, input_dimensions)
    fine_mesh = (fine_mesh - 0.5) / (mesh_size - 1) + point  # for 11 x 11
    # fine_mesh = (fine_mesh - 0.5) / (mesh_size - 1) * (fine_mesh_size -1 ) / fine_mesh_size + point # for 21 x 5
    fine_mesh = np.clip(fine_mesh, 0, 1)
    # TODO remove existing training from fine mesh
    fine_mesh = remove_existing_training(fine_mesh, training_inputs)

    return fine_mesh


def remove_existing_training(mesh, training_inputs):
    """
    Remove existing training points from the mesh.
    """

    mesh_tuples = {tuple(x) for x in mesh}
    training_tuples = {tuple(x) for x in training_inputs}
    new_mesh_tuples = mesh_tuples - training_tuples
    new_mesh = np.array(list(new_mesh_tuples))

    return new_mesh


def add_more_data(inputs, targets, new_inputs, new_targets):
    """
    Add new data to the existing data.
    """

    inputs = np.concatenate([inputs, new_inputs.reshape(1, -1)])
    targets = np.concatenate([targets, new_targets])

    return inputs, targets


def save_results(
        output_dir,
        inputs,
        targets,
        objectives,
        application
):
    """
    Save the results to a csv file.
    """

    os.makedirs(output_dir, exist_ok = True)

    with open(f"{output_dir}/results.csv", "w", newline = '') as f:
        writer = csv.writer(f)
        writer.writerow(application.input_headers + application.output_headers + ["objective function"])
        for i in range(len(targets)):
            writer.writerow(inputs[i].tolist() + targets[i].tolist() + [objectives[i]])


def save_best(
        output_dir,
        best_input,
        best_target,
        best_objective,
        application
):
    """
    Save the best result to a csv file.
    """

    os.makedirs(output_dir, exist_ok = True)

    with open(f"{output_dir}/best.csv", "w", newline = '') as f:
        writer = csv.writer(f)
        writer.writerow(application.input_headers + application.output_headers + ["objective function"])
        writer.writerow(best_input.tolist() + best_target.tolist() + [best_objective])
