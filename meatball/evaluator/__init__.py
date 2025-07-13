# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

from .evaluator import (
    default_functions,
    evaluate_expression,
    lambda_is_foo,
    lambda_is_str_eq,
    lambda_upper,
)

__all__ = [
    "evaluate_expression",
    "default_functions",
    "lambda_upper",
    "lambda_is_str_eq",
    "lambda_is_foo",
]
