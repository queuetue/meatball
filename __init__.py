# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

from .core.evaluator import (
    default_functions,
    evaluate_expression,
    lambda_is_foo,
    lambda_upper,
)
from .core.parser import parse_expression
from .core.plugins import PLUGIN_REGISTRY, get_macro, register_macro
from .preprocessor import preprocess_yaml_file, preprocess_yaml_string

__all__ = [
    "preprocess_yaml_file",
    "preprocess_yaml_string",
    "parse_expression",
    "evaluate_expression",
    "default_functions",
    "lambda_upper",
    "lambda_is_foo",
    "register_macro",
    "get_macro",
    "PLUGIN_REGISTRY",
]
