# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

"""
Macro registry and management system.
"""

from typing import Any, Dict, Optional

from .context import ContextResolver
from .engines import MacroEngine


class MacroRegistry:
    """Central registry for macro engines and functions."""

    def __init__(self):
        self.engines: Dict[str, MacroEngine] = {}
        self.global_functions: Dict[str, Any] = {}
        self._setup_default_engines()

    def _setup_default_engines(self):
        """Set up the default macro engines."""
        from .sexpr_engine import SExpressionMacroEngine
        from .standard_engines import (
            GoTemplateMacroEngine,
            JavaScriptMacroEngine,
            JQMacroEngine,
            PyStringMacroEngine,
            UtilityMacroEngine,
        )

        # Register standard engines
        self.register_engine(PyStringMacroEngine())
        self.register_engine(JavaScriptMacroEngine())
        self.register_engine(GoTemplateMacroEngine())

        # Function-based engines
        jq_engine = JQMacroEngine()
        util_engine = UtilityMacroEngine()
        sexpr_engine = SExpressionMacroEngine()
        sexpr_engine.add_builtin_functions()

        self.register_engine(jq_engine)
        self.register_engine(util_engine)
        self.register_engine(sexpr_engine)

        # Also register their functions globally
        self.global_functions.update(jq_engine.functions)
        self.global_functions.update(util_engine.functions)
        self.global_functions.update(sexpr_engine.functions)

        # Register template engines as functions too
        py_engine = self.get_engine('py')
        js_engine = self.get_engine('js')
        go_engine = self.get_engine('go')

        if py_engine:
            def py_template_func(*args, **kwargs):
                # Get context from kwargs if available, otherwise from args
                context = kwargs.get('context')
                if context is None and args and isinstance(args[-1], dict):
                    template = ' '.join(str(arg) for arg in args[:-1])
                    context = ContextResolver(args[-1])
                elif context is None:
                    template = ' '.join(str(arg) for arg in args)
                    context = ContextResolver({})
                else:
                    template = ' '.join(str(arg) for arg in args)
                return py_engine.evaluate(template, context)
            self.global_functions['py'] = py_template_func

        if js_engine:
            def js_template_func(*args):
                if len(args) >= 2 and isinstance(args[-1], dict):
                    template = ' '.join(str(arg) for arg in args[:-1])
                    context = args[-1]
                    return js_engine.evaluate(template, ContextResolver(context))
                else:
                    template = ' '.join(str(arg) for arg in args)
                    return js_engine.evaluate(template, ContextResolver({}))
            self.global_functions['js'] = js_template_func
            self.global_functions['javascript'] = js_template_func

        if go_engine:
            def go_template_func(*args):
                if len(args) >= 2 and isinstance(args[-1], dict):
                    template = ' '.join(str(arg) for arg in args[:-1])
                    context = args[-1]
                    return go_engine.evaluate(template, ContextResolver(context))
                else:
                    template = ' '.join(str(arg) for arg in args)
                    return go_engine.evaluate(template, ContextResolver({}))
            self.global_functions['go'] = go_template_func

    def register_engine(self, engine: MacroEngine):
        """Register a macro engine."""
        self.engines[engine.name] = engine

    def register_function(self, name: str, func: Any):
        """Register a global function."""
        self.global_functions[name] = func

    def get_engine(self, name: str) -> Optional[MacroEngine]:
        """Get a macro engine by name."""
        return self.engines.get(name)

    def evaluate_macro(self, engine_name: str, expression: str, context: Dict[str, Any]) -> Any:
        """Evaluate a macro using the specified engine."""
        engine = self.get_engine(engine_name)
        if not engine:
            return f"Unknown macro engine: {engine_name}"

        context_resolver = ContextResolver(context)
        return engine.evaluate(expression, context_resolver)

    def evaluate_sexpr(self, expression: str, context: Dict[str, Any]) -> Any:
        """Evaluate an s-expression macro."""
        return self.evaluate_macro("sexpr", expression, context)

    def evaluate_function(self, func_name: str, args: list, context: Dict[str, Any]) -> Any:
        """Evaluate a function call with arguments."""
        if func_name not in self.global_functions:
            return f"Unknown function: {func_name}"

        func = self.global_functions[func_name]
        try:
            # Handle context-aware functions
            if func_name in ('f', 'fstring', 'js', 'go'):
                context_resolver = ContextResolver(context)
                return func(*args, context_resolver)
            else:
                return func(*args)
        except Exception as e:
            return f"Function error: {e}"

    def list_engines(self) -> list:
        """List all registered engines."""
        return list(self.engines.keys())

    def list_functions(self) -> list:
        """List all registered functions."""
        return list(self.global_functions.keys())


# Global registry instance
DEFAULT_REGISTRY = MacroRegistry()
