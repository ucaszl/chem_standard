from typing import List

from chem_standard.rules.path_rule import PathRule


class CompositeRule(PathRule):
    """
    Combine multiple PathRule objects.

    mode:
    - "all": all rules must allow the path
    - "any": at least one rule must allow the path
    """

    def __init__(self, rules: List[PathRule], mode: str = "all"):
        self.rules = rules
        if mode not in ("all", "any"):
            raise ValueError("mode must be 'all' or 'any'")
        self.mode = mode

    def is_path_allowed(self, path) -> bool:
        if self.mode == "all":
            return all(rule.is_path_allowed(path) for rule in self.rules)
        else:
            return any(rule.is_path_allowed(path) for rule in self.rules)

