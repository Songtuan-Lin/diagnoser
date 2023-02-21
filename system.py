import copy
from typing import Tuple, List, Set, Dict, Optional
from fd.pddl import pddl_file
from fd.pddl.tasks import Task
from fd.pddl.actions import Action
from fd.pddl.conditions import Literal, Atom
from fd.pddl.conditions import Conjunction
from component import CompPrec, CompEffAdd, CompEffDel, Component
from fd.pddl.pddl_types import TypedObject
from utils import TypeDGraph, find_all_tuples

VarSubstitution =  List[Tuple[Action, Dict[str, TypedObject]]]

class DiagnosisInfo:
    def __init__(self, result : bool, 
                 atom : Optional[Literal], 
                 idx : Optional[int]) -> None:
        """Information for checking whether a candidate set of components
        is a diagnosis

        Args:
            result (bool): Checking result
            atom (Optional[Literal]): The unsatisfied atom if the result is False
            idx (Optional[int]): The index of the action in the plan that is 
            not applicable if the result is False
        """
        # atom can be either positive (i.e., Atom) or negative (i.e., NegatedAtom) 
        self.result = result
        self.atom = atom
        self.idx = idx

class Infos:
    def __init__(self, 
                 infos : List[DiagnosisInfo]) -> None:
        self.infos = infos
        self.result = True
        for info in self.infos:
            if not info.result:
                self.result = False
                break
class System:
    def __init__(self, domain_file : str, 
                 task_files : List[str], 
                 plan_files : List[str]) -> None:
        self._systems = []
        zipped_files = zip(task_files, plan_files)
        for task_file, plan_file in zipped_files:
            system_single = self.SystemSingle(
                    domain_file, task_file, plan_file)
            self._systems.append(system_single)
    
    def is_diagnosis(self, 
                     candidate : Set[Component]) -> Infos:
        infos = []
        for syt in self._systems:
            info = syt.is_diagnosis(candidate)
            infos.append(info)
        return Infos(infos)
    
    def find_conflict(self, 
                      candidate : Set[Component], 
                      infos : Infos) -> List[Set[Component]]:
        conflicts = []
        for syt, info in zip(self._systems, infos.infos):
            if info.result:
                continue
            conflicts.append(syt.find_conflict(candidate, info))
        return conflicts
    
    def get_task(self) -> Task:
        return self._systems[0].task

    class SystemSingle:
        def __init__(self, domain_file : str, 
                     task_file : str, 
                     plan_file : str):
            """Constructing a system object

            Args:
                domain_file (str): Path to a domain file
                task_file (str): Path to a task file
                plan_file (str): Path to a plan file
            """
            self.task = pddl_file.open(task_file, domain_file)
            self.constants = list(self.task.constants) # constants in the planning problem
            # mapping action names to Action objects 
            self.name_to_action = {a.name: a for a in self.task.actions}
            # mapping object names to TypedObject objects
            self.name_to_object = {o.name: o for o in self.task.objects}
            # mapping object names to the respective types
            self.object_to_type = {o.name: o.type for o in self.task.objects}
            # type graph for storing subtype relations
            self.type_graph = TypeDGraph(self.task.types)
            try:
                with open(plan_file, "r") as pf:
                    lines = pf.readlines()
                    self.plan = [lines[idx].strip() for idx in range(len(lines)) if lines[idx].strip()]
            except FileNotFoundError:
                print("File {} does not exist".format(plan_file))
            if self.plan[-1][0] == ";":
                self.plan.pop(-1)
            # computing variable substitution functions for each action in the plan
            self._get_substitutions()

        def _is_prec_sat(self, action : Action, 
                         substitution : VarSubstitution, 
                         s : Set[Literal]) -> Optional[Literal]:
            """Deciding whether an action's precondition is satisfied in a state, provided 
            the respective variable substitution function

            Args:
                action (Action): An action
                substitution (VarSubstitution): A variable substitution function
                s (Set[Literal]): A state

            Returns:
                Optional[Literal]: An unsatisfied atom if there exists any, None
                otherwise
            """
            literals = (action.precondition,)
            if isinstance(action.precondition, Conjunction):
                literals = action.precondition.parts
            for literal in literals:
                grounded_paras = tuple(substitution[para].name for para in literal.args)
                atom = Atom(literal.predicate, grounded_paras)
                if (not literal.negated) and (atom not in s):
                    return atom
                if (literal.negated) and (atom in s):
                    return atom.negate() # return a negated atom to indicate that it shall be deleted
            return None

        def _group_comps(self, candidate : Set[Component]) -> Dict[str, List[Component]]:
            """Grouping a candidate set of components by their target action schemas' names

            Args:
                candidate (Set[Component]): A set of components 

            Returns:
                Dict[str, List[Component]]: A dictionary
            """
            group_by_action = {}
            for comp in candidate:
                if comp.action_name in group_by_action:
                    group_by_action[comp.action_name].append(comp)
                else:
                    group_by_action[comp.action_name] = [comp]
            return group_by_action

        def _next_state(self, action : Action, substitution :  VarSubstitution, state : Set[Literal]) -> None:
            """Computing the next state after applying an action in a state.

            Args:
                action (Action): An action
                substitution (VarSubstitution): A variable substitution function
                state (Set[Literal]): A state
            """
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
            
        def _get_substitutions(self) -> None:
            """Computing the variable substitution functions for each action in the plan.
            
            """
            self.substitutions = []
            for a in self.plan:
                if a[0] == "(" and a[-1] == ")":
                    a = a[1:-1]
                parts = a.split(" ")
                action = self.name_to_action[parts[0]]
                assert(len(action.parameters) == len(parts) - 1)
                var_map = {p.name: self.name_to_object[parts[idx + 1]] for idx, p in enumerate(action.parameters)}
                for p in action.parameters:
                    assert(self.type_graph.subtype(var_map[p.name].type, p.type))
                var_map.update([(c.name, c) for c in self.constants])
                self.substitutions.append((action, var_map))

        def _matching(self, parts : List[Literal], substitution : VarSubstitution, atom : Literal) -> Set[Literal]:
            """Computing all atoms in some action schema which can be grounded to a
            given proposition under a provided variable substitution function.

            Args:
                parts (List[Literal]): A list of atoms
                substitution (VarSubstitution): A variable substitution function
                atom (Literal): A grounded atom

            Returns:
                Set[Literal]: A set of atoms
            """
            atoms = set()
            for literal in parts:
                grounded_paras = tuple(substitution[para].name for para in literal.args)
                target = Atom(literal.predicate, grounded_paras)
                if literal.negated:
                    target = target.negate()
                if target == atom:
                    atoms.add(literal)
            return atoms

        def _matching_prec(self, 
                        action : Action, 
                        substitution: VarSubstitution, 
                        atom : Literal) -> Set[Literal]:
            """Computing a set of atoms that can be removed from the action schema's
            (specified by the index in the plan) precondition, provided a proposition
            in some action's precondition that is not satisfied.

            Args:
                action (Action): an action schema
                substitution (VarSubstitution): a variable substitution function
                atom (Literal): A grounded atom

            Returns:
                Set[Literal]: A set of atoms
            """
            literals = (action.precondition, )
            if isinstance(action.precondition, Conjunction):
                literals = action.precondition.parts
            return self._matching(literals, substitution, atom)

        def _matching_neg_effs(self, 
                            action: Action, 
                            substitution: VarSubstitution, 
                            atom : Literal) -> Set[Literal]:
            """Computing a set of atoms that can be deleted from the action schema's
            (specified by the index in the plan) negative effects provided a proposition
            in some action's precondition that is not satisfied.

            Args:
                action (Action): an action schema
                substitution (VarSubstitution): a variable substitution function
                atom (Literal): A grounded atom

            Returns:
                Set[Literal]: A set of atoms
            """
            del_effs = [eff.literal.negate() for eff in action.effects if eff.literal.negated]
            return self._matching(del_effs, substitution, atom)
        
        def _matching_pos_effs(self, 
                            action: Action, 
                            substitution: VarSubstitution, 
                            atom : Literal) -> Set[Literal]:
            """Computing a set of atoms that can be deleted from the action schema's
            (specified by the index in the plan) positive effects provided a proposition
            in some action's precondition that is not satisfied.

            Args:
                action (Action): an action schema
                substitution (VarSubstitution): a variable substitution function
                atom (Literal): A grounded atom

            Returns:
                Set[Literal]: A set of atoms
            """
            pos_effs = [eff.literal for eff in action.effects if not eff.literal.negated]
            return self._matching(pos_effs, substitution, atom)

        def _matching_add_effs(self, 
                            action: Action, 
                            substitution: VarSubstitution, 
                            atom : Literal) -> Set[Literal]:
            """Finding a set of atoms (either positive or negative) that can be
            added to an action schema's (specified by the idx in plan) effects
            (either positive or negative), provided the proposition (either
            positive or negative) in some action's precondition that is not
            satisfied.

            Args:
                action (Action): an action schema
                substitution (VarSubstitution): a variable substitution function
                atom (Literal): Grounded atom

            Returns:
                Set[Literal]: A set of (lifted) atoms
            """
            # can be further optimized
            matched_paras = []
            for o in atom.args:
                paras = []
                for para in action.parameters:
                    if self.type_graph.subtype(self.object_to_type[o], para.type):
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

        def _get_repaired_action(
                self, action : Action, 
                repairs_to_actions : Dict[str, List[Component]]) -> Action:
            """Apply repairs to an action

            Args:
                action (Action): An action to be repaired
                repairs_to_actions (Dict[str, List[Component]]): A group of repairs
                    targeted at the action

            Returns:
                Action: _description_
            """
            if action.name in repairs_to_actions:
                for comp in repairs_to_actions[action.name]:
                    action = comp.apply(action)
            return action

        def is_diagnosis(self, candidate : Set[Component]) -> DiagnosisInfo:
            """Deciding whether a candidate set of components is a diagnosis.

            Args:
                candidate (Set[Component]): A set of candidate components

            Returns:
                DiagnosisInfo: Information about the test
            """
            self.cache = []
            repairs_to_actions = self._group_comps(candidate)
            s = set(self.task.init.copy())
            for idx, (action, substitution) in enumerate(self.substitutions):
                action = self._get_repaired_action(action, repairs_to_actions)
                # self.cache.append(action)
                # decide whether the action's precondition is satisfied
                unsat_atom = self._is_prec_sat(action, substitution, s)
                if unsat_atom is not None:
                    return DiagnosisInfo(False, unsat_atom, idx)
                self._next_state(action, substitution, s)
            # is goal satisfied
            for atom in self.task.goal.parts:
                if (not atom.negated) and (atom not in s):
                    return DiagnosisInfo(False, atom, len(self.substitutions))
                if (atom.negated) and (atom in s):
                    return DiagnosisInfo(False, atom, len(self.substitutions))
            return DiagnosisInfo(True, None, None)

        def find_conflict(self, candidate : Set[Component], info : DiagnosisInfo) -> Set[Component]:
            """Computing a conflict provided a candidate set of components and 
            the information from the last checking.

            Args:
                candidate (Set[Component]): A set of candidate components
                info (DiagnosisInfo): Information from the last check

            Returns:
                Set[Component]: A conflict
            """
            atom, idx = info.atom, info.idx
            conflict = set()
            assert(idx <= len(self.substitutions))
            repairs_to_action = self._group_comps(candidate)
            if idx != len(self.substitutions):
                action, substitution = self.substitutions[idx]
                action = self._get_repaired_action(action, repairs_to_action)
                atoms = self._matching_prec(action, substitution, atom)
                for a in atoms:
                    conflict.add(CompPrec(action.name, a))
            for i in range(idx - 1, -1, -1):
                action, substitution = self.substitutions[i]
                action = self._get_repaired_action(action, repairs_to_action)
                if not atom.negated:
                    conf_add_atoms = self._matching_add_effs(action, substitution, atom)
                else:
                    conf_add_atoms = [a.negate() for a in self._matching_add_effs(action, 
                                                                                substitution, 
                                                                                atom.negate())]
                has_neg_conf = False
                for a in conf_add_atoms:
                    comp = CompEffAdd(action.name, a)
                    conflict.add(comp)
                    for c in comp.negate():
                        if c in candidate:
                            has_neg_conf = True
                            break
                if not atom.negated:
                    conf_del_atoms = [a.negate() for a in self._matching_neg_effs(action, 
                                                                                substitution, 
                                                                                atom)]
                else:
                    conf_del_atoms = self._matching_pos_effs(action, substitution, atom.negate())
                if len(conf_del_atoms) > 0:
                    for a in conf_del_atoms:
                        conflict.add(CompEffDel(action.name, a))
                    break
                if has_neg_conf:
                    break
            cached = set()
            for c in candidate:
                if isinstance(c, CompPrec):
                    continue
                neg_confs = c.negate()
                for neg_conf in neg_confs:
                    if neg_conf in conflict:
                        c_copy = copy.copy(c)
                        conflict.add(c_copy)
                        # conflict.add(c)
                        # c.is_condition = True
                        c_copy.is_condition = True
                        conflict.remove(neg_conf)
                        cached.add(c_copy)
                        assert(c_copy.is_condition)
            for c in candidate:
                if (c in conflict) and (c not in cached):
                    conflict.remove(c)
            return conflict

if __name__ == "__main__":
    pass