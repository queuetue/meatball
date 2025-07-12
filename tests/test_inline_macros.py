# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

import unittest

from meatball.preprocessor import preprocess_yaml_string


class TestInlineMacros(unittest.TestCase):
    def setUp(self):
        self.context = {'session': {'PLANTANGENET': 'foo', 'id': 'bar'}}
        self.context_simple = {'foo': 'hello'}

    def get_key(self, result):
        if isinstance(result, dict) and 'key' in result:
            return result['key']
        return result

    def test_js_inline_macro(self):
        yaml_str = 'key: js:"${session[PLANTANGENET]}/scripts/check_local.js"'
        result = preprocess_yaml_string(yaml_str, self.context)
        self.assertEqual(self.get_key(result), 'foo/scripts/check_local.js')

    def test_go_inline_macro(self):
        yaml_str = 'key: go:"{{ .session.PLANTANGENET }}/scripts/check_local.js"'
        result = preprocess_yaml_string(yaml_str, self.context)
        self.assertEqual(self.get_key(result), 'foo/scripts/check_local.js')

    def test_py_inline_macro(self):
        yaml_str = 'key: py:"{session.id}/bar"'
        result = preprocess_yaml_string(yaml_str, self.context)
        self.assertEqual(self.get_key(result), 'bar/bar')


if __name__ == '__main__':
    unittest.main()
