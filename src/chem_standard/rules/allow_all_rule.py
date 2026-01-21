from chem_standard.rules.reaction_rule import ReactionRule


class AllowAllRule(ReactionRule):
    def is_applicable(self, reaction) -> bool:
        return True

