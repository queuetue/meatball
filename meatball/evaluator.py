# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

import os


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
    }


# Helper for lambdas in macros (for tests)
def lambda_upper(x):
    return x.upper()


def lambda_is_foo(x):
    return x == 'foo'


def lambda_is_str_eq(x):
    return x == 'foo'


def evaluate_expression(parsed, context=None, functions=None):
    if context is None:
        context = {}
    if functions is None:
        functions = default_functions()

    if isinstance(parsed, str):
        # Simple string with possible f-string interpolation
        return parsed.format(**context)

    if isinstance(parsed, list):
        fn = parsed[0]
        args = [evaluate_expression(arg, context, functions)
                for arg in parsed[1:]]

        if fn not in functions:
            raise ValueError(f"Unknown function: {fn}")

        return functions[fn](*args)

    raise TypeError(f"Unsupported type: {type(parsed)}")
