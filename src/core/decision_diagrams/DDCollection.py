from __future__ import annotations

import json
from pathlib import Path
from typing import Set, Dict, Any

from core.BooleanFunctionCollection import BooleanFunctionCollection
from core.decision_diagrams.DD import DD


class DDCollection(BooleanFunctionCollection):

    def __init__(self, dds: Set[DD] = None):
        super().__init__(dds)

    def get_input_variables(self) -> Set[str]:
        raise NotImplementedError()

    def get_output_variables(self) -> Set[str]:
        raise NotImplementedError()

    def get_auxiliary_variables(self) -> Set[str]:
        raise NotImplementedError()

    def to_json(self) -> Dict[Any, Any]:
        return {
            "dds": [dd.to_json() for dd in self.boolean_functions]
        }

    def write(self, file_path: Path) -> Dict[str, Any]:
        json_content = self.to_json()
        json_string = json.dumps(json_content, indent=6)
        with open(file_path, "w") as f:
            f.write(json_string)
            f.write("\n")

    def add(self, dd: DD):
        super().add(dd)

    def prune(self) -> DDCollection:
        new_dd_collection = DDCollection()
        for dd in self.boolean_functions:
            new_dd = dd.prune()
            new_dd_collection.add(new_dd)
        return new_dd_collection
