# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

import unittest

from meatball.evaluator import default_functions, evaluate_expression


class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.context = {'session': {'PLANTANGENET': 'foo'}}
        self.functions = default_functions()

    def test_f_string_interpolation(self):
        expr = '{session[PLANTANGENET]}/scripts/check_local.js'
        context = {'session': {'PLANTANGENET': 'foo'}}
        result = evaluate_expression(expr, context)
        self.assertEqual(result, 'foo/scripts/check_local.js')

    def test_concat_function(self):
        expr = ['concat', 'foo', '/bar.js']
        result = evaluate_expression(expr)
        self.assertEqual(result, 'foo/bar.js')

    def test_upper_function(self):
        expr = ['upper', 'foo']
        result = evaluate_expression(expr)
        self.assertEqual(result, 'FOO')

    def test_lower_function(self):
        expr = ['lower', 'FOO']
        result = evaluate_expression(expr)
        self.assertEqual(result, 'foo')

    def test_env_function(self):
        import os
        os.environ['TEST_VAR'] = 'bar'
        expr = ['env', 'TEST_VAR']
        result = evaluate_expression(expr)
        self.assertEqual(result, 'bar')

    def test_unknown_function(self):
        expr = ['notafunc', 'foo']
        with self.assertRaises(ValueError):
            evaluate_expression(expr)

    def test_unsupported_type(self):
        expr = {'foo': 'bar'}
        with self.assertRaises(TypeError):
            evaluate_expression(expr)


if __name__ == '__main__':
    unittest.main()
