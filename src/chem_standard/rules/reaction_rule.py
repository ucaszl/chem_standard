from abc import ABC, abstractmethod


class ReactionRule(ABC):
    @abstractmethod
    def is_applicable(self, reaction) -> bool:
        """
        Decide whether a reaction is allowed.
        """
        pass
