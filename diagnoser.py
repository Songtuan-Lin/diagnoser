import pddl_parser
import memhitter

from system import System

class Diagnoser:
    def __init__(self, system):
        self.system = system
        self.idx_to_comp, self.comp_to_idx = {}, {}

    def diagnosis(self):
        hitter = memhitter.Hitter()
        while True:
            candidate = hitter.top()
            candidate = set(self.idx_to_comp[x] for x in candidate)
            info = self.system.is_diagnosis(candidate)
            if info.result:
                return candidate
            conf = self.system.find_conflict(candidate, info)
            conflict = []
            for c in conf:
                if c not in self.comp_to_idx:
                    idx = len(self.comp_to_idx) + 1
                    self.comp_to_idx[c] = idx
                    self.idx_to_comp[idx] = c
                conflict.append(self.comp_to_idx[c])
            hitter.add_conflict(conflict)
    
if __name__ == "__main__":
    system = System("domain.pddl", "p18.pddl", "sas_plan") 
    diagnoser = Diagnoser(system)
    diagnoser.system.task.actions[1].effects.pop(1)
    diagnoser.system.task.actions[2].effects.pop(2)
    diagnoser.system.task.actions[0].effects.pop(1)
    d = diagnoser.diagnosis()
    for c in d:
        print(c)