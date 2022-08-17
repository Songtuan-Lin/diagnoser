import memhitter
import options
import os
from system import System

class Diagnoser:
    def __init__(self, system):
        self.system = system
        self.idx_to_comp, self.comp_to_idx = {}, {}

    def diagnosis(self):
        mem = []
        hitter = memhitter.Hitter()
        i = 0
        while True:
            candidate = hitter.top()
            candidate = set(self.idx_to_comp[x] for x in candidate)
            info = self.system.is_diagnosis(candidate)
            if info.result:
                return candidate
            conf = self.system.find_conflict(candidate, info)
            # mem.append(conf)
            # print("================================")
            # print("- Iteration: {}".format(i))
            # for c in conf:
            #     print(c)
            # print("----------")
            # print("- Conflicts")
            # for c in mem:
            #     print(c)
            conflict = []
            for c in conf:
                if c not in self.comp_to_idx:
                    idx = len(self.comp_to_idx) + 1
                    self.comp_to_idx[c] = idx
                    self.idx_to_comp[idx] = c
                if c.is_condition:
                    conflict.append(-self.comp_to_idx[c])
                else:
                    conflict.append(self.comp_to_idx[c])
            hitter.add_conflict(conflict)
            i += 1

class DiagnoserMult:
    def __init__(self, system_mult):
        self.system_mult = system_mult
        self.idx_to_comp, self.comp_to_idx = {}, {}

    def diagnosis(self):
        hitter = memhitter.Hitter()
        while True:
            candidate = hitter.top()
            candidate = set(self.idx_to_comp[x] for x in candidate)
            infos = self.system_mult.is_diagnosis(candidate)
            if infos.result:
                return candidate
            confs = self.system_mult.find_conflict(candidate, infos)
            for conf in confs:
                conflict = []
                for c in conf:
                    if c not in self.comp_to_idx:
                        idx = len(self.comp_to_idx) + 1
                        self.comp_to_idx[c] = idx
                        self.idx_to_comp[idx] = c
                    if c.is_condition:
                        conflict.append(-self.comp_to_idx[c])
                    else:
                        conflict.append(self.comp_to_idx[c])
                hitter.add_conflict(conflict)

    
if __name__ == "__main__":
    syt = System(options.domain, options.task, options.plan) 
    diagnoser = Diagnoser(syt)
    d = diagnoser.diagnosis()
    print("******************************************")
    for c in d:
        print(c)
    # for idx, a in enumerate(syt.task.actions):
    #         for c in d:
    #             if a.name == c.action_name:
    #                 syt.task.actions[idx] = c.apply(syt.task.actions[idx])

    # with open(os.path.join(options.out_dir, "domain-repaired.pddl"), "w") as f:
    #     f.write(syt.task.domain())