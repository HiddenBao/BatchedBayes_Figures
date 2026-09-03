"""File containing arguments definitions for parsing commandline arguments (or config file arguments)"""

import argparse


def define_parser():
    parser = argparse.ArgumentParser()

    # define the argument options here

    # Example:
    # parser.add_argument(
    # "--argument_tag",
    # type=int,
    # default=10,
    # help="Description of the option. Default is default_value."
    # )

    # Could also do choices from a list:
    # parser.add_argument(
    # "--option_tag",
    # choices=["option1", "option2"],
    # default="option1",
    # help="Description of the option. Default is option1.
    # )

# -----------------------------------------------------------------------------
# Program Options
# -----------------------------------------------------------------------------

    parser.add_argument(
        "--seed",
        type = int,
        default = 0,
        help = "The random seed to use. Default is 0."
    )
    parser.add_argument(
        "--output_dir",
        default = "results",
        help = "The directory to save the output files. Default is results.",
    )

    ### Initial Data Options
    parser.add_argument(
        "--num_initial_data",
        type = int,
        default = 10,
        help = "The number of initial data points to use. Default is 10.",
    )
    parser.add_argument(
        "--initial_inputs_method",
        choices = [
            "random",
            "latin_hypercube",
            "sobol"
        ],
        default = "latin_hypercube",
        help = "The method for choosing the initial guesses. Default is latin_hypercube.",
    )
# -----------------------------------------------------------------------------
# Sampling and Choice Options
# -----------------------------------------------------------------------------

    parser.add_argument(
        "--mesh_size",
        type = int,
        default = 11,
        help = "The number of points to consider in each dimension. Default is 21. Because it's a many dimensional grid, array of points can become very large.",
    )
    parser.add_argument(
        "--fine_mesh_size",
        type = int,
        default = 21,
        help = "The number of points to consider in each dimension for the fine mesh, within one step of the regular mesh. Not to be used for general sampling, just local refinement around a chosen point. Default is 21.",
    )
    parser.add_argument(
        "--qmc_samples",
        type = int,
        default = 512,
        help = "The number of QMC samples to use. Default is 512.",
    )
    parser.add_argument(
        "--num_selected_data",
        type = int,
        default = 10,
        help = "The number of data points to select and add to the training set after initial data. Default is 10. Excludes the final greedy choice.",
    )
    parser.add_argument(
        "--choice_method",
        choices = ["expected_improvement"],
        default = "expected_improvement",
        help = "The type of surrogate model to use. Default is expected_improvement.",
    )
    parser.add_argument(
        "--no_final_choice",
        action = "store_true",
        help = "If this flag is set, the final greedy choice will not be made.",
    )
    parser.add_argument(
        "--top_k_categories",
        type = int,
        default = 10,
        help = "Number of discrete categories (K) to keep after the coarse pass"
    )
    parser.add_argument(
        "--batch_size",
        type = int,
        default = 1,
        help = "Number of new points to suggest in each BO iteration. Default is 1.",
    )
    parser.add_argument(
        "--batch_method",
        choices=["hallucinated", "thompson", "greedy_ei_screening"],
        default='hallucinated',
        help="Method to use for batch selection. Default is 'hallucinated'."
    )
    parser.add_argument(
        "--max_per_category",
        type=int,
        default=0,
        help="Maximum proposals from the same categorical combination (thompson and greedy_ei_screening). "
             "0 means no limit for thompson; treated as 1 for greedy_ei_screening. Default is 0.",
    )
    ### Surrogate Model Options
    parser.add_argument(
        "--surrogate_model_type",
        choices=["updated_surrogate"],
        default="updated_surrogate",
        help="The type of surrogate model to use. Default is updated_surrogate.",
    )
    parser.add_argument(
        "--surrogate_model_target",
        choices = ["components"],
        default = "components",
        help = "The target of the surrogate model. Default is components except for Parzen when it defaults to objectives.",
    )
    parser.add_argument(
        "--target",
        type = float,
        default = 2,
        help = "The target value for the PE term in the objective function. Default is 2.",
    )
    parser.add_argument(
        "--application_class",
        choices = ["microemulsion"],
        default = "microemulsion",
        help = "The class of application to use. Default is microemulsion.",
    )

    return parser


def parse_args():
    """Use the parser to parse the commandline arguments and return the namespace object."""
    parser = define_parser()
    # parse the commandline arguments
    args = parser.parse_args()
    # args is a namespace object, where each value is an attribute of the args object
    # Example: args.argument_tag = 10
    return args
