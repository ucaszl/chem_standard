from dataclasses import dataclass
from typing import Tuple
from src.identity.reaction_identity import ReactionIdentity

@dataclass(frozen=True)
class ReactionSignature:
    """
    Canonical, order-invariant signature of a chemical reaction.

    A ReactionSignature represents *what we believe makes two reactions equivalent*,
    independent of:
    - atom ordering
    - molecule ordering
    - reaction_id
    - metadata
    """

    reactants: Tuple[str, ...]
    products: Tuple[str, ...]

    def canonical_tuple(self) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        """
        Deterministic tuple representation used for hashing and comparison.
        """
        return (
            tuple(sorted(self.reactants)),
            tuple(sorted(self.products)),
        )

    def canonical_key(self) -> str:
        """
        Stable string key derived from canonical_tuple.
        """
        return repr(self.canonical_tuple())

    def identity(self) -> ReactionIdentity:
        """
        Build a ReactionIdentity under the canonical scheme.

        Current version: v1
        """
        return ReactionIdentity(
            scheme="canonical",
            version="v1",
            canonical_key=self.canonical_key(),
        )