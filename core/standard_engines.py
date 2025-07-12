# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT
"""
Standard macro engines for the Meatball system.
"""

import os
import re
from typing import Any

from .context import ContextResolver
from .engines import FunctionMacroEngine, TemplateMacroEngine


class PyStringMacroEngine(TemplateMacroEngine):
    """Python format-string style macro engine: {variable}"""

    def __init__(self):
        super().__init__("py")

    def convert_template_syntax(self, template: str) -> str:
        # Remove surrounding quotes if present
        if template.startswith('"') and template.endswith('"'):
            template = template[1:-1]
        return template


class JavaScriptMacroEngine(TemplateMacroEngine):
    """JavaScript template style macro engine: ${variable}"""

    def __init__(self):
        super().__init__("js")

    def convert_template_syntax(self, template: str) -> str:
        """Convert ${var} to {session[PLANTANGENET]} or {var}"""
        # Remove surrounding quotes if present
        if template.startswith('"') and template.endswith('"'):
            template = template[1:-1]
        # Convert ${...} to {...}
        return re.sub(r'\$\{([^}]+)\}', r'{\1}', template)


class GoTemplateMacroEngine(TemplateMacroEngine):
    """Go template style macro engine: {{ .variable }}"""

    def __init__(self):
        super().__init__("go")

    def convert_template_syntax(self, template: str) -> str:
        """Convert {{ .var }} to {session[PLANTANGENET]} or {var}"""
        # Remove surrounding quotes if present
        if template.startswith('"') and template.endswith('"'):
            template = template[1:-1]
        # Convert {{ .session.PLANTANGENET }} to {session[PLANTANGENET]}
        return re.sub(r'\{\{\s*\.([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\s*\}\}', r'{session[\2]}', template)


class JQMacroEngine(FunctionMacroEngine):
    """jq-style data transformation functions."""

    def __init__(self):
        super().__init__("jq")
        self._setup_jq_functions()

    def evaluate(self, expression: str, context: ContextResolver, *args, **kwargs) -> Any:
        """Evaluate jq expression (function call)."""
        # For direct function evaluation
        if expression in self.functions:
            return self.functions[expression]
        return f"Unknown jq function: {expression}"

    def _setup_jq_functions(self):
        """Set up jq-style transformation functions."""
        self.functions.update({
            'map': self._map,
            'filter': self._filter,
            'select': self._select,
            'get': self._get,
            'length': self._length,
            'keys': self._keys,
            'values': self._values,
            'sort': self._sort,
            'reverse': self._reverse,
            'group_by': self._group_by,
            'unique': self._unique,
            'flatten': self._flatten,
        })

    def _map(self, func, data):
        """Map function over data."""
        from .registry import DEFAULT_REGISTRY
        if isinstance(func, str):
            # Try to resolve function from global registry
            fn = DEFAULT_REGISTRY.global_functions.get(func)
            if fn:
                return [fn(item) for item in data]
            # Simple attribute access fallback
            return [getattr(item, func, None) if hasattr(item, func) else item.get(func) for item in data]
        return [func(item) for item in data]

    def _filter(self, func, data):
        """Filter data with function."""
        from .registry import DEFAULT_REGISTRY
        if isinstance(func, str):
            fn = DEFAULT_REGISTRY.global_functions.get(func)
            if fn:
                return [item for item in data if fn(item)]
            # Simple attribute/key check fallback
            return [item for item in data if (hasattr(item, func) and getattr(item, func)) or (isinstance(item, dict) and item.get(func))]
        return [item for item in data if func(item)]

    def _select(self, data, key):
        """Select value by key."""
        if isinstance(data, dict):
            return data.get(key)
        return getattr(data, key, None)

    def _get(self, data, key, default=None):
        """Get value with default."""
        if isinstance(data, dict):
            return data.get(key, default)
        return getattr(data, key, default)

    def _length(self, data):
        """Get length of data."""
        return len(data)

    def _keys(self, data):
        """Get keys of dict."""
        if isinstance(data, dict):
            return list(data.keys())
        return []

    def _values(self, data):
        """Get values of dict."""
        if isinstance(data, dict):
            return list(data.values())
        return []

    def _sort(self, data):
        """Sort data."""
        return sorted(data)

    def _reverse(self, data):
        """Reverse data."""
        return list(reversed(data))

    def _group_by(self, func, data):
        """Group data by function result."""
        from itertools import groupby
        if isinstance(func, str):
            def key_func(x): return x.get(func) if isinstance(
                x, dict) else getattr(x, func, None)
        else:
            key_func = func
        # Sort data first, handling None values
        try:
            sorted_data = sorted(data, key=lambda x: key_func(x) or '')
        except TypeError:
            # Fallback for non-comparable types
            sorted_data = data
        return {k: list(g) for k, g in groupby(sorted_data, key=key_func)}

    def _unique(self, data):
        """Get unique items."""
        return list(set(data))

    def _flatten(self, data):
        """Flatten nested lists."""
        result = []
        for item in data:
            if isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result


class UtilityMacroEngine(FunctionMacroEngine):
    """Utility functions for common operations."""

    def __init__(self):
        super().__init__("util")
        self._setup_utility_functions()

    def evaluate(self, expression: str, context: ContextResolver, *args, **kwargs) -> Any:
        """Evaluate utility expression (function call)."""
        # For direct function evaluation
        if expression in self.functions:
            return self.functions[expression]
        return f"Unknown utility function: {expression}"

    def _setup_utility_functions(self):
        """Set up utility functions."""
        self.functions.update({
            'concat': self._concat,
            'upper': self._upper,
            'lower': self._lower,
            'strip': self._strip,
            'replace': self._replace,
            'split': self._split,
            'join': self._join,
            'env': self._env,
            'default': self._default,
        })

    def _concat(self, *args):
        """Concatenate strings."""
        return ''.join(str(arg) for arg in args)

    def _upper(self, text):
        """Convert to uppercase."""
        return str(text).upper()

    def _lower(self, text):
        """Convert to lowercase."""
        return str(text).lower()

    def _strip(self, text):
        """Strip whitespace."""
        return str(text).strip()

    def _replace(self, text, old, new):
        """Replace text."""
        return str(text).replace(old, new)

    def _split(self, text, sep=None):
        """Split text."""
        return str(text).split(sep)

    def _join(self, sep, items):
        """Join items with separator."""
        return sep.join(str(item) for item in items)

    def _env(self, var, default=''):
        """Get environment variable."""
        return os.getenv(var, default)

    def _default(self, value, default_value):
        """Return default if value is None or empty."""
        return default_value if not value else value
