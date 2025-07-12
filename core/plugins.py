# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

"""
Meatball S-expression plugin system
----------------------------------
Register new macro functions for s-expression evaluation.
"""

PLUGIN_REGISTRY = {}


def register_macro(name, fn):
    """Register a new macro function for s-expressions."""
    PLUGIN_REGISTRY[name] = fn


def get_macro(name):
    return PLUGIN_REGISTRY.get(name)


# Example: register a custom macro
register_macro('reverse', lambda s: s[::-1])

# Usage in evaluator:
# functions = {**default_functions(), **PLUGIN_REGISTRY}
