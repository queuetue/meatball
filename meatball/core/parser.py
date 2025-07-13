# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

import sexpdata


def parse_expression(expr):
    """
    Parse a string s-expression into a sexpdata AST.
    E.g. "(concat a b)" -> [Symbol('concat'), Symbol('a'), Symbol('b')]
    """
    return sexpdata.loads(expr)
