import argparse
import sys
from importlib.metadata import version

arg_parser = argparse.ArgumentParser(
    prog="validate_version", description="Validate that the package version matches a value"
)
arg_parser.add_argument("-e", "--expected_version", type=str, required=True, help="The expected version")
args = arg_parser.parse_args()

installed_version = version("alpyki")
expected_version = args.expected_version[1:] if args.expected_version.startswith("v") else args.expected_version

if installed_version != expected_version:
    print(f"Installed version: {installed_version}, but expected: {expected_version}", file=sys.stderr)
    exit(1)
