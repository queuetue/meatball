# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT


import ast
import os
import re

import sexpdata


def js_macro(s, *args, **context):
    # Replace JS-style ${var} with Python-style {var}
    s = re.sub(r'\$\{([a-zA-Z0-9_\.]+)\}', r'{\1}', s)
    if args and isinstance(args[0], dict):
        context = args[0]
    result = s.format(**context)
    # Remove any $ directly preceding a context value
    result = re.sub(r'\$(\w+)', r'\1', result)
    # Strip leading '$' if present after interpolation
    if result.startswith('$'):
        result = result[1:]
    return result


def go_macro(s, *args, **context):
    # Replace Go-style {{ .var }} with Python-style {var}
    s = re.sub(r'\{\{\s*\.([a-zA-Z0-9_]+)\s*\}\}', r'{\1}', s)
    if args and isinstance(args[0], dict):
        context = args[0]
    return s.format(**context)


def fstring_macro(s, *args, **context):
    # Accept context as either positional or keyword
    if args and isinstance(args[0], dict):
        context = args[0]
    return s.format(**context)


def hy_macro(expr, *args, **context):
    try:
        import hy
        # Remove extra quotes if present
        if expr.startswith('"') and expr.endswith('"'):
            expr = expr[1:-1]
        # Try to evaluate as a single s-expression
        try:
            result = hy.eval(expr)
            return result
        except Exception:
            # Fallback: try to compile and exec as a module
            import types

            from hy.compiler import hy_compile
            hy_compiled = hy_compile(expr, '__main__')
            if isinstance(hy_compiled, tuple):
                hy_ast = hy_compiled[1]
            else:
                hy_ast = hy_compiled
            code_obj = compile(hy_ast, '<hy_macro>', 'exec')
            module = types.ModuleType('__main__')
            exec(code_obj, module.__dict__)
            return getattr(module, '_hy_last', None)
    except Exception as e:
        return f"Error: {e}"


def lupy_macro(expr, *args, **context):
    try:
        from lupy import eval as lupy_eval
        # Remove extra quotes if present
        if expr.startswith('"') and expr.endswith('"'):
            expr = expr[1:-1]
        # Evaluate s-expression with context
        return lupy_eval(expr, context)
    except Exception as e:
        return f"Error: {e}"


def default_functions():
    return {
        'concat': lambda *args: ''.join(args),
        'upper': lambda s: s.upper(),
        'lower': lambda s: s.lower(),
        'env': lambda var, default='': os.getenv(var, default),
        'map': lambda fn, lst: [fn(x) for x in lst],
        'filter': lambda fn, lst: [x for x in lst if fn(x)],
        'select': lambda d, k: d[k],
        'length': lambda x: len(x),
        'get': lambda d, k, default=None: d.get(k, default),
        'f': fstring_macro,
        'fstring': fstring_macro,
        'js': js_macro,
        'javascript': js_macro,
        'go': go_macro,
        'gostring': go_macro,
        'hy': hy_macro,
        'lupy': lupy_macro,
    }

# Helper for lambdas in macros (for tests)


def lambda_upper(x):
    return x.upper()


def lambda_is_foo(x):
    return x == 'foo'


def evaluate_expression(parsed, context=None, functions=None):
    if context is None:
        context = {}
    if functions is None:
        functions = default_functions()

    # sexpdata AST: function application
    if isinstance(parsed, list):
        fn = parsed[0]
        # Resolve function name
        if isinstance(fn, sexpdata.Symbol):
            fn_name = fn.value()
        else:
            fn_name = fn
        # Special handling for map/filter: resolve first arg to callable
        args = []
        for i, arg in enumerate(parsed[1:]):
            val = evaluate_expression(arg, context, functions)
            if fn_name in ('map', 'filter') and i == 0:
                if isinstance(val, str) and val in functions:
                    val = functions[val]
                elif isinstance(val, sexpdata.Symbol) and val.value() in functions:
                    val = functions[val.value()]
            # For get/select, ensure first arg is a dict
            if fn_name in ('get', 'select') and i == 0:
                if isinstance(val, str):
                    try:
                        val = ast.literal_eval(val)
                    except Exception:
                        pass
            args.append(val)
        if fn_name not in functions:
            raise ValueError(f"Unknown function: {fn_name}")
        # Pass context to f/fstring macros
        if fn_name in ('f', 'fstring'):
            return functions[fn_name](*args, context)
        # For length, ensure argument is a list
        if fn_name == 'length' and isinstance(args[0], str):
            try:
                args[0] = ast.literal_eval(args[0])
            except Exception:
                pass
        # For concat, ensure all args are strings
        if fn_name == 'concat':
            args = [str(a) for a in args]
        return functions[fn_name](*args)

    # sexpdata Symbol: resolve from functions or context
    if isinstance(parsed, sexpdata.Symbol):
        name = parsed.value()
        if name in functions:
            return functions[name]
        # Dot notation: session.PLANTANGENET
        if '.' in name:
            try:
                parts = name.split('.')
                val = context
                for part in parts:
                    val = val[part]
                return val
            except Exception:
                return f"Error: '{name}'"
        # Bracket notation: session[PLANTANGENET]
        if '[' in name and name.endswith(']'):
            try:
                base, key = name.split('[', 1)
                key = key[:-1]
                val = context.get(base, {})
                return val[key]
            except Exception:
                return f"Error: '{name}'"
        # Plain symbol: context lookup
        return context.get(name, name)

    # String: try to parse as literal, else format
    if isinstance(parsed, str):
        stripped = parsed.strip()
        if (stripped.startswith('{') and stripped.endswith('}')) or \
           (stripped.startswith('[') and stripped.endswith(']')):
            try:
                return ast.literal_eval(parsed)
            except Exception:
                return parsed
        return parsed.format(**context)

    # Numbers, booleans, etc.
    return parsed
