from abc import ABC, abstractmethod
from src.reaction import Reaction


class ReactionRule(ABC):
    """
    Abstract base class for reaction feasibility rules.

    A ReactionRule decides whether a reaction is allowed
    under a specific chemical principle.
    """

    @abstractmethod
    def is_applicable(self, reaction: Reaction) -> bool:
        """
        Return True if the reaction satisfies this rule.
        """
        raise NotImplementedError
