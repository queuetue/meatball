# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT
"""
S-expression macro engine for advanced macro support.
"""

from typing import Any

import sexpdata

from .context import ContextResolver
from .engines import FunctionMacroEngine


class SExpressionMacroEngine(FunctionMacroEngine):
    """S-expression based macro engine with robust parsing and evaluation."""

    def __init__(self):
        super().__init__("sexpr")

    def parse(self, expression: str) -> Any:
        """Parse s-expression string into AST using sexpdata."""
        try:
            return sexpdata.loads(expression)
        except Exception as e:
            raise ValueError(f"S-expression parse error: {e}")

    def evaluate(self, expression: str, context: ContextResolver, *args, **kwargs) -> Any:
        """Evaluate s-expression with context."""
        try:
            parsed = self.parse(expression)
            return self._evaluate_ast(parsed, context)
        except Exception as e:
            return f"S-expression error: {e}"

    def _sexp_to_native(self, value):
        import sexpdata
        if isinstance(value, sexpdata.Brackets):
            # Convert Brackets to list
            return [self._sexp_to_native(v) for v in value.I]
        if isinstance(value, sexpdata.Quoted):
            # For quoted strings, return the string without quotes
            inner = self._sexp_to_native(value.x)
            if isinstance(inner, str):
                # Remove trailing quote if present
                return inner.rstrip("'")
            return inner
        if isinstance(value, list):
            return [self._sexp_to_native(v) for v in value]
        if isinstance(value, sexpdata.Symbol):
            symbol_val = value.value()
            # Remove trailing quote if present in symbol
            if isinstance(symbol_val, str):
                return symbol_val.rstrip("'")
            return symbol_val
        return value

    def _evaluate_ast(self, ast: Any, context: ContextResolver) -> Any:
        """Evaluate parsed s-expression AST."""
        # List: function application (func arg1 arg2 ...)
        if isinstance(ast, list):
            if not ast:
                return []

            func_expr = ast[0]
            args = ast[1:]

            # Resolve function
            if isinstance(func_expr, sexpdata.Symbol):
                func_name = func_expr.value()
            else:
                func_name = str(func_expr)

            # Evaluate arguments
            eval_args = [self._evaluate_ast(arg, context) for arg in args]

            # Built-in functions
            if func_name in self.functions:
                native_args = [self._sexp_to_native(a) for a in eval_args]
                return self.functions[func_name](*native_args)

            # Try to resolve from context
            func = context.resolve(func_name)
            if callable(func):
                native_args = [self._sexp_to_native(a) for a in eval_args]
                return func(*native_args)

            # Try to get from global registry
            from .registry import DEFAULT_REGISTRY
            if func_name in DEFAULT_REGISTRY.global_functions:
                fn = DEFAULT_REGISTRY.global_functions[func_name]
                native_args = [self._sexp_to_native(a) for a in eval_args]
                # Special handling for filter/map: resolve first arg to callable if string
                if func_name in ('filter', 'map') and native_args:
                    first = native_args[0]
                    if isinstance(first, str):
                        f = DEFAULT_REGISTRY.global_functions.get(first)
                        if f:
                            native_args[0] = f
                # Special handling for template engines: pass context
                if func_name in ('py', 'f', 'fstring', 'js', 'javascript', 'go'):
                    native_args.append(context.context)
                return fn(*native_args)

            raise ValueError(f"Unknown function: {func_name}")

        # Symbol: variable lookup
        if isinstance(ast, sexpdata.Symbol):
            symbol_val = ast.value()
            # If symbol looks like a path or literal, return as-is
            if symbol_val.startswith('/') or symbol_val.startswith('.'):
                return symbol_val
            # Otherwise, always resolve from context
            resolved = context.resolve(symbol_val)
            return resolved

        # Quoted expressions - they're actually just the quoted value directly
        if hasattr(ast, 'quote'):
            return ast

        # Literals (strings, numbers, etc.)
        return ast

    def add_builtin_functions(self):
        """Add commonly used built-in functions."""
        self.functions.update({
            '+': lambda *args: sum(args),
            '-': lambda a, b=None: -a if b is None else a - b,
            '*': lambda *args: self._multiply(*args),
            '/': lambda a, b: a / b,
            '=': lambda a, b: a == b,
            '<': lambda a, b: a < b,
            '>': lambda a, b: a > b,
            'list': lambda *args: list(args),
            'dict': lambda *args: dict(args[i:i+2] for i in range(0, len(args), 2)),
            'if': self._if,
            'when': self._when,
            'cond': self._cond,
        })

    def _multiply(self, *args):
        """Multiply all arguments."""
        result = 1
        for arg in args:
            result *= arg
        return result

    def _if(self, condition, true_expr, false_expr=None):
        """Conditional expression."""
        return true_expr if condition else false_expr

    def _when(self, condition, *expressions):
        """Execute expressions when condition is true."""
        if condition:
            return expressions[-1] if expressions else None
        return None

    def _cond(self, *clauses):
        """Multi-way conditional (cond (test1 expr1) (test2 expr2) ...)"""
        for clause in clauses:
            if isinstance(clause, list) and len(clause) >= 2:
                test, expr = clause[0], clause[1]
                if test:
                    return expr
        return None
