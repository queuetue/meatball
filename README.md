# Meatball

A minimal, pluggable tool for expanding macros in YAML files safely and clearly.

Traditional YAML workflows often rely on ad-hoc Jinja, shell replacements, or hidden scripts that make configurations brittle and opaque. Meatball defines a clear, explicit, and safe macro-expansion system that is pluggable and auditable. It helps teams manage complexity by offering sandboxed interpreters, easy plugin registration, and consistent syntax across use cases.

This makes infrastructure and application configuration both safer and more maintainable.

---

## Table of Contents

1. [Install](#install)
2. [Purpose and Overview](#purpose-and-overview)
3. [Support and Community](#support-and-community)
4. [Macro Forms](#macro-forms)

   * [1. Inline Macros](#1-inline-macros)
   * [2. S-expression Macros](#2-s-expression-macros)
   * [3. List Macros](#3-list-macros)
   * [4. Explicit Engine/Template Block](#4-explicit-enginetemplate-block)
5. [Pipeline Processing](#pipeline-processing)
6. [Plugin System and Extensibility](#plugin-system-and-extensibility)
7. [Integration & Comparison](#integration--comparison)
8. [Future Directions](#future-directions)
9. [Security Model](#security-model)
10. [Testing](#testing)
11. [CLI Usage](#cli-usage)
12. [License](#license)

---

## Install

Requires **Python 3.8+**.

```bash
pip install git+https://github.com/queuetue/meatball.git
```

---

## Purpose and Overview

Meatball formalizes YAML macro expansion in a safe, declarative, and inspectable way.

### Goals

* Formal, declarative macro expansion
* Clear, consistent configuration transformations
* No hidden scripts or arbitrary code execution
* Easy plugin system for adding engines

---

**Quick Example:**

```yaml
greeting: py:"Hello, {name}!"
```

---

Typical use cases include configuration management, templated deployments, and maintaining consistent variable substitutions across large YAML files. This approach emphasizes clarity, safety, and maintainability in configuration design.

---

## Support and Community

Meatball is part of the **Plantangenet Project**, a broader effort to build formal, structured tools for managing complexity in systems design and configuration.

If you'd like to support ongoing development, visit our [Patreon](https://patreon.com/c/plantangenet).

---

## Macro Forms

Meatball supports multiple styles of macro expansion to suit different needs and YAML design preferences.

---

### 1. Inline Macros

Best for simple, one-line substitutions with minimal syntax overhead.

```yaml
script_path: js:"${session[PLANTANGENET]}/scripts/check_local.js"
config_path: go:"{{ .session.PLANTANGENET }}/scripts/check_local.js"
greeting: py:"Hello, {name}!"
```

---

### 2. S-expression Macros

Designed for nested, composable forms that express more complex templating logic clearly.

```yaml
script_path: expr:'(js "${session[PLANTANGENET]}/scripts/check_local.js")'
config_path: expr:'(go "{{ .session.PLANTANGENET }}/scripts/check_local.js")'
joined_path: expr:'(concat foo /bar.js)'
greeting: expr:'(py "Hello, {name}!")'
```

*Note: single quotes in YAML help avoid escaping issues.*

---

### 3. List Macros

Clear, explicit, and easy to format across multiple lines.

```yaml
script_path:
  - js
  - "${session[PLANTANGENET]}/scripts/check_local.js"

config_path:
  - go
  - "{{ .session.PLANTANGENET }}/scripts/check_local.js"

joined_path:
  - concat
  - foo
  - /bar.js

rpn_example:
  - foo
  - /bar.js
  - concat

greeting:
  - py
  - "Hello, {name}!"
```

---

### 4. Explicit Engine/Template Block

Recommended for clarity, especially with complex or multiline templates.

```yaml
script_path:
  engine: js
  template: "${session[PLANTANGENET]}/scripts/check_local.js"

config_path:
  engine: go
  template: "{{ .session.PLANTANGENET }}/scripts/check_local.js"

greeting:
  engine: py
  template: "Hello, {name}!"
```

---

## Pipeline Processing

Real-world YAML workflows often involve several transformations in sequence. Meatball's pipeline system lets you define clear, modular steps that operate one after another. Each step receives the modified data and a context object, making it easy to implement staged processing.

*A pipeline is a sequence of Python functions that transform the loaded YAML data.*

For example:

```python
def double_cpu(data, ctx):
    data['cpu'] *= 2
    return data

def compute_cost(data, ctx):
    data['cost'] = data['cpu'] * 0.12
    return data

result = run_pipeline(yaml_content, steps=[double_cpu, compute_cost])
```

The pipeline framework ensures the original YAML is available for audit in `context['_original_yaml']`, supporting safe, clear transformation design.

---

## Plugin System and Extensibility

Plugins are discovered at runtime by registering them in your code or imported packages. You control when and how they are available.

For example, in a deployment pipeline you might register a custom `mustache` engine:

```python
from meatball.core.plugins import register_engine

def mustache_engine(template, context):
    # Your rendering logic here
    return ...

register_engine('mustache', mustache_engine)
```

**Usage in YAML:**

```yaml
greeting: mustache:"Hello, {{name}}!"
```

**Note:** Register your plugins before performing macro expansion to ensure availability.

---

## Integration & Comparison

You can compare expanded and original YAML fields to verify correctness—useful for auditing, testing, or CI pipelines.

**Example:**

Original YAML:

```yaml
script_path: js:"${session[PLANTANGENET]}/scripts/check_local.js"
```

Expanded YAML:

```yaml
script_path: "/home/ciuser/scripts/check_local.js"
```

**Python usage:**

```python
from meatball.integrations.yaml_compare import compare_yaml_field

processed, original = compare_yaml_field(yaml_content, 'script_path')
```

Returns a tuple of `(processed_value, original_template)` for easy test assertions.

---

## Future Directions

* Additional macro engines (Mustache, Jinja2) for broader compatibility
* Linting and static analysis for macros
* GitOps-friendly change detection
* Locking for concurrent processing to support multi-threaded CI/CD

---

## Security Model

Meatball emphasizes safety by design:

* **Sandboxed interpreters** (no file access, limited execution scope)
* **No arbitrary code execution**
* **Only explicit, context-driven interpolation**
* Designed for **safe, declarative configuration**

---

## Testing

Examples in `meatball/tests/` cover:

* Macro expansion forms
* S-expressions and list macros
* Pipeline chaining
* Plugin registration
* Integration and comparison

**Run tests:**

```bash
pip install pytest
pytest meatball/tests/
```

---

## CLI Usage

Meatball offers a command-line interface so you can preprocess YAML files directly—ideal for shell scripts, CI/CD, or local development.

**Example usage:**

```bash
python -m meatball your-config.yaml -c context.json > processed.yaml
```

**CLI Implementation Example:**

```python
import argparse
import sys
import json
import yaml
from meatball import preprocess_yaml_file

def main():
    parser = argparse.ArgumentParser(description='Meatball - macro-expansion preprocessor for YAML')
    parser.add_argument('input', help='Input YAML file')
    parser.add_argument('-c', '--context', help='JSON file with context variables', default=None)
    args = parser.parse_args()

    context = {}
    if args.context:
        with open(args.context) as f:
            context = json.load(f)

    processed = preprocess_yaml_file(args.input, context)
    yaml.dump(processed, sys.stdout, sort_keys=False)
```

---

## License

MIT
