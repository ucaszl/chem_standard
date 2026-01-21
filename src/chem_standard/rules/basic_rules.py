from chem_standard.rules.reaction_rule import ReactionRule


class NonEmptyReactionRule(ReactionRule):
    """
    Reject reactions with empty reactants or products.
    """

    def is_applicable(self, reaction):
        return bool(reaction.reactants) and bool(reaction.products)

