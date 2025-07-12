# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

"""
Clean, modular macro preprocessor for the Meatball system.
"""

from typing import Any, Dict, Optional

import yaml

from .registry import DEFAULT_REGISTRY


class MacroPreprocessor:
    """
    Clean macro preprocessor with support for:
    - S-expression macros: (function arg1 arg2)
    - Prefixed macros: f:, js:, go:, expr:
    - Template engines with proper context resolution
    """

    def __init__(self, registry=None):
        self.registry = registry or DEFAULT_REGISTRY

    def process_yaml(self, yaml_content: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Process YAML content with macro expansion."""
        if context is None:
            context = {}
        # Store original YAML in context for downstream use
        context['_original_yaml'] = yaml_content
        # Parse YAML first
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parse error: {e}")
        # Merge parsed data into context for macro resolution
        if isinstance(data, dict):
            context.update(data)
        # Process the parsed data
        return self.process_value(data, context)

    def process_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Process a value, expanding any macros found."""
        if isinstance(value, str):
            return self._process_string(value, context)
        elif isinstance(value, list):
            # RPN-style list macro: [engine, expression]
            if value and isinstance(value[0], str) and value[0] in self.registry.list_engines():
                engine_name = value[0]
                expr = value[1] if len(value) > 1 else ''
                return self.registry.evaluate_macro(engine_name, expr, context)
            # Regular list processing
            return [self.process_value(item, context) for item in value]
        elif isinstance(value, dict):
            # Check for inline macro form: {engine: "template"}
            new_dict = {}
            for key, val in value.items():
                if key in self.registry.list_engines() and isinstance(val, str):
                    # Rewrite to prefixed macro form
                    macro_str = f'{key}:{val}'
                    new_dict['key'] = self._process_string(macro_str, context)
                else:
                    new_dict[key] = self.process_value(val, context)
            return new_dict
        else:
            return value

    def _process_string(self, value: str, context: Dict[str, Any]) -> Any:
        """Process a string value for macro expansion."""
        value = value.strip()

        # Skip if marked as literal
        if value.startswith('*'):
            return value

        # Handle prefixed macros
        for prefix in ['py:', 'js:', 'go:', 'expr:']:
            if value.startswith(prefix):
                return self._process_prefixed_macro(value, prefix, context)

        # Handle s-expression macros
        if value.startswith('(') and value.endswith(')'):
            return self._process_sexpr_macro(value, context)

        # No macro detected, return as-is
        return value

    def _process_prefixed_macro(self, value: str, prefix: str, context: Dict[str, Any]) -> Any:
        """Process a prefixed macro (f:, js:, go:, expr:)."""
        expression = value[len(prefix):].strip()

        if prefix == 'expr:':
            # expr: is an alias for s-expression
            expression = expression.strip('"').strip("'")
            return self.registry.evaluate_sexpr(expression, context)
        else:
            # Template engines
            engine_name = prefix[:-1]  # Remove the ':'
            return self.registry.evaluate_macro(engine_name, expression, context)

    def _process_sexpr_macro(self, value: str, context: Dict[str, Any]) -> Any:
        """Process an s-expression macro."""
        return self.registry.evaluate_sexpr(value, context)


# Global preprocessor instance
DEFAULT_PREPROCESSOR = MacroPreprocessor()


def process_yaml(yaml_content: str, context: Optional[Dict[str, Any]] = None) -> Any:
    """Convenience function for processing YAML with the default preprocessor."""
    return DEFAULT_PREPROCESSOR.process_yaml(yaml_content, context)


def process_value(value: Any, context: Optional[Dict[str, Any]] = None) -> Any:
    """Convenience function for processing a value with the default preprocessor."""
    if context is None:
        context = {}
    return DEFAULT_PREPROCESSOR.process_value(value, context)
