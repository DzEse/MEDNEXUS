import argparse
from mednexus.pipeline import run

parser = argparse.ArgumentParser(description='Run the MEDNEXUS analytical pipeline.')
parser.add_argument('--clean', action='store_true', help='Rebuild generated outputs from scratch.')
parser.add_argument('--seed', type=int, default=None, help='Override random seed.')
args = parser.parse_args()

run(clean=args.clean, seed=args.seed)
