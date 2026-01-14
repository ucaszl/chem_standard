from dataclasses import dataclass


@dataclass(frozen=True)
class ReactionIdentity:
    """
    Stable identity for a chemical reaction under a given canonicalization scheme.

    Fields:
    - scheme: identity scheme name (e.g. 'canonical')
    - version: canonicalization version (e.g. 'v1')
    - canonical_key: hash value representing the reaction
    """
    scheme: str
    version: str
    canonical_key: str

    @property
    def full_id(self) -> str:
        """
        Return the full stable identifier string.

        Example:
        canonical:v1:668a814e0dc00654...
        """
        return f"{self.scheme}:{self.version}:{self.canonical_key}"

    def __str__(self) -> str:
        return self.full_id

    def to_dict(self) -> dict:
        return {
            "scheme": self.scheme,
            "version": self.version,
            "canonical_key": self.canonical_key,
            "full_id": self.full_id,
        }
