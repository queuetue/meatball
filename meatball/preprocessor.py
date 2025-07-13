# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

# Shim preprocessor to use new core
from meatball.core.preprocessor import DEFAULT_PREPROCESSOR


def preprocess_yaml_string(yaml_str, context=None):
    """Process YAML string with macro expansion."""
    return DEFAULT_PREPROCESSOR.process_yaml(yaml_str, context or {})


def preprocess_yaml_file(filepath, context=None):
    """Process a YAML file with macro expansion."""
    with open(filepath) as f:
        yaml_str = f.read()
    return preprocess_yaml_string(yaml_str, context)
