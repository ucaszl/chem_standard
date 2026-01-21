from abc import ABC, abstractmethod
from typing import List


class PathRule(ABC):
    @abstractmethod
    def is_path_allowed(self, path: List) -> bool:
        """
        Decide whether the current path is allowed to continue.
        Path format:
        [species, reaction, species, reaction, ..., species]
        """
        pass
