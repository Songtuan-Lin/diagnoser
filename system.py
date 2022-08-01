import sys
import os
sys.path.append(os.path.join(os.getcwd(), "downward", "src", "translate"))

import pddl_parser
import pddl
from pddl.conditions import Atom
from pddl.conditions import Conjunction
from component import ComponentPrec, ComponentPosEff, ComponentNegEff
from utils import TypeDGraph, find_all_tuples

class DiagnosisInfo:
    def __init__(self, result, atom, idx):
        self.result = result
        self.atom = atom
        self.idx = idx

class System:
    def __init__(self, domain_file, task_file, plan_file):
        self.task, self.constants = self.__parse(domain_file, task_file)
        self.name_to_action = {a.name: a for a in self.task.actions}
        self.name_to_object = {o.name: o for o in self.task.objects}
        self.object_to_type = {o.name: o.type_name for o in self.task.objects}
        self.type_graph = TypeDGraph(self.task.types)
        try:
            with open(plan_file, "r") as pf:
                lines = pf.readlines()
                self.plan = [lines[idx].strip() for idx in range(len(lines)) if lines[idx].strip()]
        except FileNotFoundError:
            print("File {} does not exist".format(plan_file))
        if self.plan[-1][0] == ";":
            self.plan.pop(-1)
        self.__get_substitutions()

    def __parse(self, domain_file, task_file):
        domain_pddl = pddl_parser.pddl_file.parse_pddl_file("domain", domain_file)
        task_pddl = pddl_parser.pddl_file.parse_pddl_file("task", task_file)

        domain_name, domain_requirements, types, type_dict, constants, predicates, predicate_dict, functions, actions, axioms = pddl_parser.parsing_functions.parse_domain_pddl(domain_pddl)

        task_name, task_domain_name, task_requirements, objects, init, goal, use_metric = pddl_parser.parsing_functions.parse_task_pddl(task_pddl, type_dict, predicate_dict)

        assert domain_name == task_domain_name
        requirements = pddl.Requirements(sorted(set(
                domain_requirements.requirements +
                task_requirements.requirements)))
        objects = constants + objects

        pddl_parser.parsing_functions.check_for_duplicates([o.name for o in objects], errmsg="error: duplicate object %r", finalmsg="please check :constants and :objects definitions")
        init += [pddl.Atom("=", (obj.name, obj.name)) for obj in objects]

        return pddl.Task(domain_name, task_name, requirements, types, objects, predicates, functions, init, goal, actions, axioms, use_metric), constants


    def __is_prec_sat(self, action, substitution, s):
        literals = (action.precondition,)
        if isinstance(action.precondition, Conjunction):
            literals = action.precondition.parts
        for literal in literals:
            grounded_paras = tuple(substitution[para].name for para in literal.args)
            atom = Atom(literal.predicate, grounded_paras)
            if atom not in s:
                return atom
        return None

    def __group_comps(self, candidates):
        group_by_action = {}
        for comp in candidates:
            if comp.action_name in group_by_action:
                group_by_action[comp.action_name].append(comp)
            else:
                group_by_action[comp.action_name] = [comp]
        return group_by_action

    def __next_state(self, action, substitution, state):
        add_effs, del_effs = set(), set()
        for eff in action.effects:
            assert(len(eff.parameters) == 0)
            literal = eff.literal
            grounded_paras = tuple(substitution[para].name for para in literal.args)
            atom = Atom(literal.predicate, grounded_paras)
            if literal.negated:
                del_effs.add(atom)
            else:
                add_effs.add(atom)
        for eff in del_effs:
            if eff in state:
                state.remove(eff)
        for eff in add_effs:
            state.add(eff)  
        
    def __get_substitutions(self):
        self.substitutions = []
        for a in self.plan:
            if a[0] == "(" and a[-1] == ")":
                a = a[1:-1]
            parts = a.split(" ")
            action = self.name_to_action[parts[0]]
            assert(len(action.parameters) == len(parts) - 1)
            var_map = {p.name: self.name_to_object[parts[idx + 1]] for idx, p in enumerate(action.parameters)}
            for p in action.parameters:
                assert(self.type_graph.subtype(var_map[p.name].type_name, p.type_name))
            var_map.update([(c.name, c) for c in self.constants])
            self.substitutions.append((action, var_map))

    def __matching(self, parts, substitution, atom):
        atoms = set()
        for literal in parts:
            grounded_paras = tuple(substitution[para].name for para in literal.args)
            if Atom(literal.predicate, grounded_paras) == atom:
                atoms.add(literal)
        return atoms

    def __matching_prec(self, idx, atom):
        atoms = set()
        action, substitution = self.substitutions[idx]
        literals = (action.precondition, )
        if isinstance(action.precondition, Conjunction):
            literals = action.precondition.parts
        return self.__matching(literals, substitution, atom)

    def __matching_del_effs(self, idx, atom):
        atoms = set()
        action, substitution = self.substitutions[idx]
        del_effs = [eff.literal.negate() for eff in action.effects if eff.literal.negated]
        return self.__matching(del_effs, substitution, atom)

    def __matching_add_effs(self, idx, atom):
        # can be further optimized
        matched_paras = []
        action, substitution = self.substitutions[idx]
        for o in atom.args:
            paras = []
            for para in action.parameters:
                if self.type_graph.subtype(self.object_to_type[o], para.type_name):
                    paras.append(para.name)
            if o in substitution:
                paras.append(o)
            if len(paras) == 0:
                return set()
            matched_paras.append(paras)
        all_tuples = find_all_tuples(matched_paras)
        re = set()
        for t in all_tuples:
            grounded_paras = tuple(substitution[v].name for v in t)
            if grounded_paras == atom.args:
                re.add(Atom(atom.predicate, t))
        return re

    def is_diagnosis(self, candidates):
        self.cache = []
        group_by_action = self.__group_comps(candidates)
        s = set(self.task.init.copy())
        for idx, (action, substitution) in enumerate(self.substitutions):
            if action.name in group_by_action:
                for comp in group_by_action[action.name]:
                    action = comp.apply(action) # apply the repair (component)
            self.cache.append(action)
            # decide whether the action's precondition is satisfied
            unsat_atom = self.__is_prec_sat(action, substitution, s)
            if unsat_atom is not None:
                return DiagnosisInfo(False, unsat_atom, idx)
            self.__next_state(action, substitution, s)
        # is goal satisfied
        for atom in self.task.goal:
            if atom not in s:
                return DiagnosisInfo(False, atom, len(self.substitutions))
        return DiagnosisInfo(True, None, None)

    def find_conflict(self, candidate, info):
        assert(info.result == False)
        conflicts = set()
        atom, idx = info.atom, info.idx
        if idx < len(self.substitutions):
            action, _ = self.substitutions[idx]
            atoms = self.__matching_prec(idx, atom)
            for a in atoms:
                conflicts.add(ComponentPrec(action.name, a))
        for i in range(idx - 1, -1, -1):
            post_action = self.cache[i]
            action, substitution = self.substitutions[i]
            conf_del_effs = self.__matching_del_effs(i, atom)
            if len(conf_del_effs) != 0:
                for a in conf_del_effs:
                    conflicts.add(ComponentNegEff(action.name, a))
                break
            conf_add_effs = self.__matching_add_effs(i, atom)
            for a in conf_add_effs:
                conflicts.add(ComponentPosEff(action.name, a))
        return conflicts - candidate


if __name__ == "__main__":
    pass