# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

import yaml as pyyaml
from meatball.core.preprocessor import process_yaml


def compare_yaml_field(yaml_content: str, field: str):
    """
    Preprocesses the YAML, then compares the value of a field in the processed and original YAML.
    Returns (processed_value, original_value).
    """
    context = {}
    processed = process_yaml(yaml_content, context)
    original_yaml = context.get('_original_yaml', '')
    original_data = pyyaml.safe_load(original_yaml) if original_yaml else {}
    processed_value = processed.get(field)
    original_value = original_data.get(field)
    return processed_value, original_value
