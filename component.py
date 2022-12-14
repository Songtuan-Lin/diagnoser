from pddl.conditions import Atom
from pddl.conditions import Conjunction
from pddl.actions import Action
from pddl.conditions import Truth
from pddl.effects import Effect

class Component:
    def __init__(self, action_name, atom):
        self.action_name = action_name
        self.atom = atom

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.action_name == other.action_name and self.atom == other.atom

    def __hash__(self):
        return hash((self.action_name, self.atom))

    def __repr__(self):
        return "{}".format(self)

    def apply(self, action):
        pass


class ComponentPrec(Component):
    def __str__(self):
        return "<Component: Remove {} from Precondition: {}>".format(self.atom, self.action_name)

    def apply(self, action):
        assert(self.action_name == action.name)
        lits = (action.precondition,)
        if isinstance(action.precondition, Conjunction):
            lits = action.precondition.parts
        new_lits = []
        for l in lits:
            if self.atom == l:
                continue
            new_lits.append(l)
        new_prec = Conjunction(new_lits)
        return Action(action.name, action.parameters, action.num_external_parameters, new_prec, action.effects, action.cost)

class ComponentPosEff(Component):
    def __str__(self):
        return "<Component: Add {} to Pos-effects: {}>".format(self.atom, self.action_name)

    def apply(self, action):
        assert(self.action_name == action.name)
        new_effs = [eff for eff in action.effects]
        new_eff = Effect([], Truth(), self.atom)
        new_effs.append(new_eff)
        return Action(action.name, action.parameters, action.num_external_parameters, action.precondition, new_effs, action.cost)

class ComponentNegEff(Component):
    def __str__(self):
        return "<Component: Remove {} from Neg-effects: {}>".format(self.atom, self.action_name)

    def apply(self, action):
        assert(self.action_name == action.name)
        new_effs = []
        for eff in action.effects:
            if eff.literal == self.atom.negate():
                continue
            new_effs.append(eff)
        return Action(action.name, action.parameters, action.num_external_parameters, action.precondition, new_effs, action.cost)