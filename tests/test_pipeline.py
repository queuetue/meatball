# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

import pytest
from meatball.core.pipeline import run_pipeline


def test_pipeline_order_and_context():
    yaml_content = '''
x: 2
y: "expr:'(+ x 3)'"
'''.strip()

    def step_a(data, ctx):
        # multiply y by 2
        data['y'] = data['y'] * 2
        return data

    def step_b(data, ctx):
        # add z as sum of x and y
        data['z'] = data['x'] + data['y']
        return data

    result = run_pipeline(yaml_content, steps=[step_a, step_b])
    assert result['x'] == 2
    assert result['y'] == 10
    assert result['z'] == 12


def test_pipeline_original_yaml_in_context():
    yaml_content = '''
    a: hello
    '''.strip()
    captured_context = {}

    def step_inspect(data, ctx):
        captured_context.update(ctx)
        return data

    result = run_pipeline(yaml_content, steps=[step_inspect])
    # context should have '_original_yaml'
    assert '_original_yaml' in captured_context
    assert captured_context['_original_yaml'].strip() == "a: hello"
    # data unchanged
    assert result['a'] == 'hello'


if __name__ == '__main__':
    pytest.main()
