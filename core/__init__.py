# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

"""
Meatball core module - clean, modular macro system.
"""

from .context import ContextResolver
from .engines import FunctionMacroEngine, MacroEngine, TemplateMacroEngine
from .preprocessor import (
    DEFAULT_PREPROCESSOR,
    MacroPreprocessor,
    process_value,
    process_yaml,
)
from .registry import DEFAULT_REGISTRY, MacroRegistry
from .sexpr_engine import SExpressionMacroEngine
from .standard_engines import (
    GoTemplateMacroEngine,
    JavaScriptMacroEngine,
    JQMacroEngine,
    PyStringMacroEngine,
    UtilityMacroEngine,
)

__all__ = [
    # Main interfaces
    'MacroPreprocessor', 'DEFAULT_PREPROCESSOR', 'process_yaml', 'process_value',
    'MacroRegistry', 'DEFAULT_REGISTRY',
    'ContextResolver',

    # Engine base classes
    'MacroEngine', 'TemplateMacroEngine', 'FunctionMacroEngine',

    # Standard engines
    'PyStringMacroEngine', 'JavaScriptMacroEngine', 'GoTemplateMacroEngine',
    'JQMacroEngine', 'UtilityMacroEngine', 'SExpressionMacroEngine',
]
