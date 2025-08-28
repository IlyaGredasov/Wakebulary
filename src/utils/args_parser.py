import argparse


def restricted_float(min_val, max_val):
    def checker(value):
        f = float(value)
        if not (min_val <= f <= max_val):
            raise argparse.ArgumentTypeError(f"Value must be between {min_val} and {max_val}")
        return f

    return checker


def parse_args():
    parser = argparse.ArgumentParser(description="English/Russian learning application")

    parser.add_argument(
        "--mode",
        choices=["eng", "rus"],
        default="rus",
        help="Mode of operation: 'eng' or 'rus' (default: eng)"
    )

    parser.add_argument(
        "--alpha",
        type=float,
        default=8.0,
        help="Alpha value that is using in expovariate distribution (default: 8.0)"
    )

    parser.add_argument(
        "--clear_delay",
        type=float,
        default=1.0,
        help="Terminal clear delay in seconds (default: 1.0)"
    )

    parser.add_argument(
        "--randomness_const",
        type=restricted_float(0.0, 1.0),
        default=1.0,
        help="Randomness constant between 0 and 1 (default: 1.0)"
    )

    parser.add_argument(
        "--sample_size",
        type=int,
        default=50,
        help="Sample size for each session (default: 50)"
    )

    return parser.parse_args()
