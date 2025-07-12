# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

import unittest

from meatball.preprocessor import preprocess_yaml_string


class TestJSMacros(unittest.TestCase):
    def setUp(self):
        self.context = {'session': {'PLANTANGENET': 'foo'}}

    def get_key(self, result):
        if isinstance(result, dict) and 'key' in result:
            return result['key']
        return result

    def test_js_macro(self):
        yaml_str = "key: expr:'(js \"${session[PLANTANGENET]}/scripts/check_local.js\")'"
        result = preprocess_yaml_string(yaml_str, self.context)
        self.assertEqual(self.get_key(result), 'foo/scripts/check_local.js')

    def test_javascript_macro(self):
        yaml_str = "key: expr:'(javascript \"${session[PLANTANGENET]}/scripts/check_local.js\")'"
        result = preprocess_yaml_string(yaml_str, self.context)
        self.assertEqual(self.get_key(result), 'foo/scripts/check_local.js')

    def test_list_js_macro(self):
        yaml_str = 'key:\n  - js\n  - "${session[PLANTANGENET]}/scripts/check_local.js"'
        result = preprocess_yaml_string(yaml_str, self.context)
        self.assertEqual(self.get_key(result), 'foo/scripts/check_local.js')

    def test_js_macro_simple_context(self):
        yaml_str = "key: expr:'(js ${foo}/bar)'"
        context = {'foo': 'hello'}
        result = preprocess_yaml_string(yaml_str, context)
        self.assertEqual(self.get_key(result), 'hello/bar')

    def test_js_macro_no_interpolation(self):
        yaml_str = "key: expr:'(js /static/path)'"
        result = preprocess_yaml_string(yaml_str)
        self.assertEqual(self.get_key(result), '/static/path')

    def test_js_macro_context_middle(self):
        yaml_str = "key: expr:'(js /foo/${bar}/baz)'"
        context = {'bar': 'X'}
        result = preprocess_yaml_string(yaml_str, context)
        self.assertEqual(self.get_key(result), '/foo/X/baz')

    def test_js_macro_context_end(self):
        yaml_str = "key: expr:'(js /foo/bar/${baz})'"
        context = {'baz': 'END'}
        result = preprocess_yaml_string(yaml_str, context)
        self.assertEqual(self.get_key(result), '/foo/bar/END')


if __name__ == '__main__':
    unittest.main()
