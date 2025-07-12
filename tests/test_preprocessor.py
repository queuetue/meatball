# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT


import unittest

from meatball.preprocessor import preprocess_yaml_string


class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        self.context = {'session': {'PLANTANGENET': 'foo'}}

    def get_key(self, result):
        if isinstance(result, dict) and 'key' in result:
            return result['key']
        return result

    def test_inline_py_macro(self):
        # Use s-expression form for py macro with quoted template
        yaml_str = "key: expr:'(py \"{session[PLANTANGENET]}/scripts/check_local.js\")'"
        result = preprocess_yaml_string(yaml_str, self.context)
        self.assertEqual(self.get_key(result), 'foo/scripts/check_local.js')

    def test_inline_concat_macro(self):
        yaml_str = "key: expr:'(concat foo /bar.js)'"
        result = preprocess_yaml_string(yaml_str)
        self.assertEqual(self.get_key(result), 'foo/bar.js')

    def test_explicit_engine_template(self):
        # This test expects the implementation to support explicit engine/template blocks
        yaml_str = 'key:\n  engine: py\n  template: "{session[PLANTANGENET]}/scripts/check_local.js"'
        result = preprocess_yaml_string(yaml_str, self.context)
        key_val = self.get_key(result)
        self.assertIsInstance(key_val, dict)
        self.assertIn('engine', key_val)
        self.assertIn('template', key_val)

    def test_list_macro(self):
        yaml_str = 'key:\n  - py\n  - "{session[PLANTANGENET]}/scripts/check_local.js"'
        result = preprocess_yaml_string(yaml_str, self.context)
        self.assertEqual(self.get_key(result), 'foo/scripts/check_local.js')

    def test_rpn_macro(self):
        yaml_str = 'key:\n  - foo\n  - /bar.js\n  - concat'
        result = preprocess_yaml_string(yaml_str)
        self.assertIsInstance(self.get_key(result), list)


if __name__ == '__main__':
    unittest.main()
