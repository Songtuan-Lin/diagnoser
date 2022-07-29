import unittest

from system import System

from pddl.conditions import Atom
from pddl.conditions import Truth
from pddl.effects import Effect

from component import ComponentPrec
from component import ComponentPosEff
from component import ComponentNegEff

from utils import TypeDGraph, find_all_tuples

class TestSystem(unittest.TestCase):
    def test_generate_tuples(self):
        test_case = [[2, 2, 3, 6], [1, 6, 8], [3, 5]]
        ground_truth = set()
        for e1 in test_case[0]:
            for e2 in test_case[1]:
                for e3 in test_case[2]:
                    ground_truth.add((e1, e2, e3))
        test_output = find_all_tuples(test_case)
        self.assertEqual(ground_truth, test_output)

    def test_match_prec(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        atom = Atom("at", ("tray2", "kitchen"))
        test_output = system._System__matching_prec(2, atom)
        self.assertEqual(test_output, {system.task.actions[-1].precondition})
        atom = Atom("ontray", ("sandw6", "tray1"))
        test_output = system._System__matching_prec(17, atom)
        print(test_output)
        self.assertEqual(test_output, {system.task.actions[4].precondition.parts[2]})

    def test_match_add_effs(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        atom = Atom("at", ("tray2", "kitchen"))
        test_output = system._System__matching_add_effs(6, atom)
        self.assertEqual(test_output, {Atom("at", ("?t", "?p2")), Atom("at", ("?t", "kitchen"))})
        test_output = system._System__matching_add_effs(4, atom)
        self.assertEqual(test_output, set())
        test_output = system._System__matching_add_effs(3, atom)
        self.assertEqual(test_output, {Atom("at", ("?t", "kitchen"))})
        atom = Atom("at", ("tray2", "table1"))
        test_output = system._System__matching_add_effs(3, atom)
        self.assertEqual(test_output, {Atom("at", ("?t", "?p"))})

    def test_match_neg_effs(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        atom = Atom("at", ("tray2", "kitchen"))
        test_output = system._System__matching_del_effs(8, atom)
        self.assertEqual(test_output, {Atom("at", ("?t", "?p1"))})
        atom = Atom("notexist", ("sandw8",))
        test_output = system._System__matching_del_effs(0, atom)
        self.assertEqual(test_output, {Atom("notexist", ("?s",))})

class TestComponent(unittest.TestCase):
    def test_remove_from_prec(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        action = system.task.actions[-1]
        atom = Atom("at", ("?t", "?p1"))
        comp = ComponentPrec(action.name, atom)
        post_action = comp.apply(action)
        self.assertEqual(post_action.precondition.parts, tuple())
        action = system.task.actions[1]
        atom = Atom("at_kitchen_bread", ("?b", ))
        comp = ComponentPrec(action.name, atom)
        post_action = comp.apply(action)
        self.assertEqual(post_action.precondition.parts, (Atom("at_kitchen_content", ("?c", )), Atom("notexist", ("?s",))))
    
    def test_add_to_pos_eff(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        action = system.task.actions[3]
        atom = Atom("at", ("?t", "?p"))
        comp = ComponentPosEff(action.name, atom)
        post_action = comp.apply(action)
        ground_truth = []
        for eff in action.effects:
            ground_truth.append(Effect([], Truth(), eff.literal))
        ground_truth.append(Effect([], Truth(), atom))
        self.assertEqual(post_action.effects, ground_truth)

    def test_remove_from_neg_eff(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        action = system.task.actions[0]
        atom = Atom("at_kitchen_bread", ("?b",))
        comp = ComponentNegEff(action.name, atom)
        post_action = comp.apply(action)
        ground_truth = action.effects[1:]
        self.assertEqual(post_action.effects, ground_truth)
        atom = Atom("at_kitchen_content", ("?c",))
        comp = ComponentNegEff(action.name, atom)
        post_action = comp.apply(action)
        ground_truth = action.effects[:1] + action.effects[2:]
        self.assertEqual(post_action.effects, ground_truth)

    def test_equality(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        action = system.task.actions[0]
        atom = Atom("at_kitchen_bread", ("?b",))
        comp_1 = ComponentNegEff(action.name, atom)
        comp_2 = ComponentNegEff(action.name, atom)
        self.assertEqual(comp_1, comp_2)
    
    def test_not_equality(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        action = system.task.actions[0]
        atom = Atom("at_kitchen_bread", ("?b",))
        comp_1 = ComponentNegEff(action.name, atom)
        comp_2 = ComponentPosEff(action.name, atom)
        self.assertFalse(comp_1 == comp_2)

class TestDiagnosis(unittest.TestCase):
    def test_decide_executablity_1(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        action = system.task.actions[0]
        # remove atom Atom("at_kitchen_sandwich", ("?s", ))
        action.effects.pop(2)
        info = system.is_diagnosis(set())
        atom = Atom("at_kitchen_sandwich", ("sandw8",))
        idx = 1
        self.assertEqual(info.atom, atom)
        self.assertEqual(info.idx, idx)

    def test_decide_executablity_2(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        action = system.task.actions[-1]
        # remove atom Atom("at", ("?t", "?p2"))
        action.effects.pop(-1)
        info = system.is_diagnosis(set())
        atom = Atom("at", ("tray2", "table1"))
        idx = 3
        self.assertEqual(info.atom, atom)
        self.assertEqual(info.idx, idx)

    def test_decide_executablity_3(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        action = system.task.actions[-1]
        # remove atom Atom("at", ("?t", "?p2"))
        action.effects.pop(-1)
        atom = Atom("at", ("?t", "?p2"))
        diagnosis = {ComponentPosEff(action.name, atom)}
        info = system.is_diagnosis(diagnosis)
        self.assertTrue(info.result)

    def test_find_conflicts(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        action = system.task.actions[-1]
        action.effects.pop(-1)
        info = system.is_diagnosis(set())
        conflicts = system.find_conflict(set(), info)
        atom_1 = Atom("at", ("?t", "?p2"))
        action_2 = system.task.actions[3]
        atom_2 = Atom("at", ("?t", "?p"))
        ground_truth = {ComponentPosEff(action.name, atom_1), ComponentPrec(action_2.name, atom_2)}
        self.assertEqual(conflicts, ground_truth)

class TestSubType(unittest.TestCase):
    def test_no_subtype(self):
        system = System("domain.pddl", "child-snack_pfile01.pddl", "sas_plan")
        type_graph = TypeDGraph(system.task.types)
        for t in system.task.types:
            self.assertTrue(type_graph.subtype(t.name, "object"))

if __name__=="__main__":
    unittest.main()