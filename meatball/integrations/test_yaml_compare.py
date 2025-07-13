# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

from meatball.integrations.yaml_compare import compare_yaml_field


def test_compare_yaml_field():
    yaml_content = '''
foo: bar
key: expr:'(concat foo /baz)'
'''
    processed, original = compare_yaml_field(yaml_content, 'key')
    assert processed == 'bar/baz'
    assert original == "expr:'(concat foo /baz)'"


if __name__ == '__main__':
    test_compare_yaml_field()
