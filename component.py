from fd.pddl.conditions import Atom
from fd.pddl.conditions import Conjunction
from fd.pddl.actions import Action
from fd.pddl.conditions import Truth
from fd.pddl.effects import Effect

class Component:
    def __init__(self, action_name, atom):
        self.action_name = action_name
        self.atom = atom
        self.is_condition = False

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.action_name == other.action_name and self.atom == other.atom

    def __hash__(self):
        return hash((self.action_name, self.atom))

    def __repr__(self):
        return "{}".format(self)
        
    def apply(self, action):
        pass

class CompPrec(Component):
    def __str__(self):
        return "<Component: Remove {} from Precondition: {} | Condition: {}>".format(self.atom, self.action_name, self.is_condition)

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

class CompEffAdd(Component):
    def __str__(self):
        return "<Component: Add {} to Effects: {} | Condition: {}>".format(self.atom, self.action_name, self.is_condition)

    def apply(self, action):
        assert(self.action_name == action.name)
        new_effs = [eff for eff in action.effects]
        new_eff = Effect([], Truth(), self.atom)
        new_effs.append(new_eff)
        return Action(action.name, action.parameters, action.num_external_parameters, action.precondition, new_effs, action.cost)

    def negate(self):
        return {CompEffDel(self.action_name, self.atom), CompEffAdd(self.action_name, self.atom.negate())}

class CompEffDel(Component):
    def __str__(self):
        return "<Component: Remove {} from Effects: {} | Condition: {}>".format(self.atom, self.action_name, self.is_condition)

    def apply(self, action):
        new_effs = []
        for eff in action.effects:
            if eff.literal == self.atom:
                continue
            new_effs.append(eff)
        return Action(action.name, action.parameters, action.num_external_parameters, action.precondition, new_effs, action.cost)

    def negate(self):
        return {CompEffAdd(self.action_name, self.atom), CompEffDel(self.action_name, self.atom.negate())}
