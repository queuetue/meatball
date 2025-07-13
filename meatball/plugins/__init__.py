# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

# Meatball core module

from .plugins import PLUGIN_REGISTRY, get_macro, register_macro

__all__ = [
    "register_macro",
    "get_macro",
    "PLUGIN_REGISTRY",
]
