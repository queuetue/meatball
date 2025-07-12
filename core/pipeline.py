# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT
"""
Pipeline and shadow-side processing for YAML documents.
"""
from typing import Any, Callable, Dict, List, Optional

from .preprocessor import MacroPreprocessor


class ShadowProcessor:
    """
    Runs a sequence of processing steps on a YAML document, preserving original content.

    Steps are callables that take (data: Any, context: Dict[str, Any]) and return new data.
    """

    def __init__(self, registry=None):
        self.preprocessor = MacroPreprocessor(registry)
        self.steps: List[Callable[[Any, Dict[str, Any]], Any]] = []

    def add_step(self, step: Callable[[Any, Dict[str, Any]], Any]) -> None:
        """Add a processing step to the pipeline."""
        self.steps.append(step)

    def run(self, yaml_content: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute the pipeline: first preprocess macros, then run each step in order.
        Returns the final data.
        """
        if context is None:
            context = {}
        # Initial macro expansion
        data = self.preprocessor.process_yaml(yaml_content, context)
        # Apply downstream steps
        for step in self.steps:
            data = step(data, context)
        return data


# Convenience function
def run_pipeline(yaml_content: str,
                 steps: Optional[List[Callable[[
                     Any, Dict[str, Any]], Any]]] = None,
                 context: Optional[Dict[str, Any]] = None,
                 registry=None) -> Any:
    """
    Run a ShadowProcessor with given steps.
    """
    processor = ShadowProcessor(registry)
    if steps:
        for s in steps:
            processor.add_step(s)
    return processor.run(yaml_content, context)
