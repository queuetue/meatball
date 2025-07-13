# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

"""
Context resolution and variable lookup for the Meatball macro system.
"""

import ast
from typing import Any, Dict, Optional


class ContextResolver:
    """Handles context variable resolution with dot notation, bracket notation, and aliasing."""

    def __init__(self, context: Optional[Dict[str, Any]] = None):
        self.context = context or {}
        self.aliases = {}

    def add_alias(self, alias: str, target: str):
        """Add an alias for context lookups."""
        self.aliases[alias] = target

    def resolve(self, name: str) -> Any:
        """
        Resolve a variable name from context.

        Supports:
        - Simple names: 'user'
        - Dot notation: 'user.name'
        - Bracket notation: 'user[name]'
        - Aliases: registered aliases
        """
        # Check aliases first
        if name in self.aliases:
            name = self.aliases[name]

        # Simple name lookup
        if '.' not in name and '[' not in name:
            return self.context.get(name, name)

        # Dot notation: user.name
        if '.' in name and '[' not in name:
            return self._resolve_dot_notation(name)

        # Bracket notation: user[name] or user["name"]
        if '[' in name and name.endswith(']'):
            return self._resolve_bracket_notation(name)

        # Fallback to simple lookup
        return self.context.get(name, name)

    def _resolve_dot_notation(self, name: str) -> Any:
        """Resolve dot notation like 'user.profile.name'."""
        try:
            parts = name.split('.')
            value = self.context
            for part in parts:
                if isinstance(value, dict):
                    value = value[part]
                else:
                    value = getattr(value, part)
            return value
        except (KeyError, AttributeError, TypeError):
            return f"Error: cannot resolve '{name}'"

    def _resolve_bracket_notation(self, name: str) -> Any:
        """Resolve bracket notation like 'user[name]' or 'data["key"]'."""
        try:
            # Split on first '['
            base_name, key_part = name.split('[', 1)
            key = key_part[:-1]  # Remove trailing ']'

            # Get base object
            base = self.context.get(base_name, {})

            # Try to evaluate key as literal (for "key" or 123)
            try:
                key = ast.literal_eval(key)
            except (ValueError, SyntaxError):
                # Key is a variable name, resolve it
                key = self.resolve(key)

            return base[key]
        except (KeyError, TypeError, IndexError):
            return f"Error: cannot resolve '{name}'"

    def update(self, new_context: Dict[str, Any]):
        """Update the context with new values."""
        self.context.update(new_context)
