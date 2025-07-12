# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

import unittest

from meatball.core.registry import DEFAULT_REGISTRY
from meatball.evaluator import lambda_is_foo, lambda_upper
from meatball.preprocessor import preprocess_yaml_string


class TestJQMacros(unittest.TestCase):
    def setUp(self):
        # Inject custom functions into registry for tests
        DEFAULT_REGISTRY.register_function('upper', lambda_upper)
        DEFAULT_REGISTRY.register_function('is_foo', lambda_is_foo)
        DEFAULT_REGISTRY.register_function('is_str_eq', lambda x: x == 'foo')

    def get_result(self, result, key='result'):
        # Helper to robustly extract the result value
        if isinstance(result, dict):
            return result.get(key)
        return result

    def test_map_macro(self):
        yaml_str = "result: \"expr:(map upper (list 'foo' 'bar' 'baz'))\""
        result = preprocess_yaml_string(yaml_str)
        self.assertEqual(self.get_result(result), ['FOO', 'BAR', 'BAZ'])

    def test_filter_macro(self):
        yaml_str = "result: \"expr:(filter is_str_eq (list 'foo' 'bar' 'foo' 'baz'))\""
        result = preprocess_yaml_string(yaml_str)
        self.assertEqual(self.get_result(result), ['foo', 'foo'])

    def test_select_macro(self):
        yaml_str = "result: \"expr:(select (dict 'foo' 1 'bar' 2) 'foo')\""
        result = preprocess_yaml_string(yaml_str)
        self.assertEqual(self.get_result(result), 1)

    def test_length_macro(self):
        yaml_str = "result: \"expr:(length (list 'foo' 'bar' 'baz'))\""
        result = preprocess_yaml_string(yaml_str)
        self.assertEqual(self.get_result(result), 3)

    def test_get_macro(self):
        yaml_str = "result: \"expr:(get (dict 'foo' 1 'bar' 2) 'baz' 42)\""
        result = preprocess_yaml_string(yaml_str)
        self.assertEqual(self.get_result(result), 42)


if __name__ == '__main__':
    unittest.main()
