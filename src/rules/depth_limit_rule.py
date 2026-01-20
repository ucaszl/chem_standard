from src.rules.path_rule import PathRule


class DepthLimitRule(PathRule):
    def __init__(self, max_steps: int):
        self.max_steps = max_steps

    def is_path_allowed(self, path) -> bool:
        # number of reactions = (len(path) - 1) // 2
        steps = (len(path) - 1) // 2
        return steps <= self.max_steps
