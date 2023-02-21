import memhitter
import options
import resource
import time
import os
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
            infos = self.system.is_diagnosis(candidate)
            if infos.result:
                return candidate
            confs = self.system.find_conflict(candidate, infos)
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
    start_time = time.process_time()
    syt = System(options.domain, options.tasks, options.plans) 
    diagnoser = Diagnoser(syt)
    d = diagnoser.diagnosis()
    end_time = time.process_time()
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if (options.evaluation
            and options.out_diagnosis is None):
        print("An output file for writting the dignosis " 
              "is required in the evaluation mode")
    if options.print:
        for c in d:
            print(c)
    if options.out_diagnosis is not None:
        out_file = os.path.join(
                options.out_diagnosis,
                "diagnosis")
        with open(out_file, "w") as f:
            for c in d:
                f.write(str(c) + "\n")
            if options.evaluation:
                elapsed_time = end_time - start_time
                f.write(str(elapsed_time) + "\n")
                f.write("memory: {}".format(float(peak/1024)))
    if options.out_domain is not None:
        out_file = os.path.join(
                options.out_domain,
                "domain-repaired.pddl")
        task = syt.get_task()
        for idx, a in enumerate(task.actions):
            for c in d:
                if a.name == c.action_name:
                    task.actions[idx] = c.apply(task.actions[idx])
        with open(out_file, "w") as f:
            f.write(task.domain())