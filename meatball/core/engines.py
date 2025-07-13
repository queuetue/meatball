# Meatball Macro System
# Copyright (c) 2025 Scott Russell (Queuetue)
# MIT License

"""
Base macro engine interface and common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .context import ContextResolver


class MacroEngine(ABC):
    """Abstract base class for macro engines."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def evaluate(self, expression: str, context: ContextResolver, *args, **kwargs) -> Any:
        """Evaluate a macro expression with the given context."""
        pass

    def __repr__(self):
        return f"<MacroEngine: {self.name}>"


class TemplateMacroEngine(MacroEngine):
    """Base class for template-based macro engines (f-string, JS, Go templates)."""

    def __init__(self, name: str, template_pattern: Optional[str] = None):
        super().__init__(name)
        self.template_pattern = template_pattern

    def convert_template_syntax(self, template: str) -> str:
        """Convert template syntax to Python format strings. Override in subclasses."""
        return template

    def _extract_variable_name(self, full_match: str) -> str:
        """
        Extract just the variable name from a template match.
        Examples:
        - 'session[PLANTANGENET]/scripts' -> 'session[PLANTANGENET]'
        - 'session.id/bar' -> 'session.id'
        - 'user' -> 'user'
        """
        import re
        # Match variable patterns: word, word[...], word.word, etc.
        # Stop at first non-variable character like /, space, etc.
        variable_match = re.match(
            r'^([a-zA-Z0-9_]+(?:\[[^\]]+\])*(?:\.[a-zA-Z0-9_]+)*)', full_match)
        if variable_match:
            return variable_match.group(1)
        return full_match

    def evaluate(self, expression: str, context: ContextResolver, *args, **kwargs) -> Any:
        """Evaluate template with context substitution."""
        # Convert template syntax if needed
        converted = self.convert_template_syntax(expression)

        # Build format context by resolving all variables
        format_context = {}

        # Extract variable names from the converted template
        import re
        # Match {content} patterns
        brace_matches = re.findall(r'\{([^}]+)\}', converted)

        for full_match in brace_matches:
            # Check if this is a simple variable or mixed content
            if '/' in full_match:
                # Mixed content like "session[PLANTANGENET]/scripts/check_local.js"
                # Extract variable part before the first /
                parts = full_match.split('/', 1)
                variable_part = parts[0]
                suffix = '/' + parts[1] if len(parts) > 1 else ''

                # Resolve the variable
                resolved_value = context.resolve(variable_part)
                if isinstance(resolved_value, str) and not resolved_value.startswith("Error:"):
                    # Replace the whole brace content with resolved value + suffix
                    full_replacement = str(resolved_value) + suffix
                    converted = converted.replace(
                        '{' + full_match + '}', full_replacement)
                else:
                    # Fallback to error
                    converted = converted.replace(
                        '{' + full_match + '}', str(resolved_value))
            else:
                # Simple variable case
                py_key = '_' + re.sub(r'[^a-zA-Z0-9_]', '_', full_match)
                converted = converted.replace(
                    '{' + full_match + '}', '{' + py_key + '}')
                format_context[py_key] = context.resolve(full_match)

        try:
            result = converted.format(**format_context)
            return result
        except (KeyError, ValueError) as e:
            return f"Template error: {e}"


class FunctionMacroEngine(MacroEngine):
    """Base class for function-based macro engines that evaluate callable expressions."""

    def __init__(self, name: str, functions: Optional[Dict[str, Any]] = None):
        super().__init__(name)
        self.functions = functions or {}

    def add_function(self, name: str, func: Any):
        """Add a function to this macro engine."""
        self.functions[name] = func

    def resolve_function(self, name: str) -> Any:
        """Resolve a function by name."""
        if name in self.functions:
            return self.functions[name]
        # Try to import built-in functions
        try:
            return eval(name)
        except Exception:
            raise ValueError(f"Unknown function: {name}")
