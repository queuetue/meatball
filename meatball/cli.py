# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

import argparse
import sys

import yaml

from preprocessor import preprocess_yaml_file


def main():
    parser = argparse.ArgumentParser(
        description='Meatball - s-expression preprocessor for YAML')
    parser.add_argument('input', help='Input YAML file')
    parser.add_argument('-c', '--context',
                        help='JSON file with context variables', default=None)

    args = parser.parse_args()

    context = {}
    if args.context:
        import json
        with open(args.context) as f:
            context = json.load(f)

    processed = preprocess_yaml_file(args.input, context)
    yaml.dump(processed, sys.stdout, sort_keys=False)
