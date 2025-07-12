# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

def parse_expression(expr):
    """
    Improved parser: turns a string s-expression into a nested list.
    E.g. "(concat a b)" -> ['concat', 'a', 'b']
    """
    import shlex
    # Normalize spaces around parentheses
    expr = expr.replace('(', ' ( ').replace(')', ' ) ')
    expr = ' '.join(expr.split())
    tokens = shlex.split(expr)

    def parse_tokens(tokens):
        if not tokens:
            raise ValueError("Unexpected EOF while parsing")
        token = tokens.pop(0)
        if token == '(':
            lst = []
            while tokens and tokens[0] != ')':
                lst.append(parse_tokens(tokens))
            if not tokens:
                raise ValueError("Missing closing parenthesis")
            tokens.pop(0)  # Remove ')'
            return lst
        elif token == ')':
            raise ValueError("Unexpected )")
        else:
            return token
    return parse_tokens(tokens)
