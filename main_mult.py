import os
import time
import logging
import resource
import traceback
import options

from system import SystemMult
from diagnoser import DiagnoserMult
from tqdm import tqdm

logging.basicConfig(filename="err.log", level=logging.DEBUG, 
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger=logging.getLogger(__name__)

if __name__ == "__main__":
    fuzzed_tasks = []
    for domain_name in os.listdir(options.benchmark_dir):
        domain_dir = os.path.join(options.benchmark_dir, domain_name)
        if not os.path.isdir(domain_dir):
            continue
        fuzzed_dir = os.path.join(domain_dir, "err-rate-{}".format(options.err_rate))
        domain_file = os.path.join(fuzzed_dir, "domain.pddl")
        task_files, plan_files = [], []
        for task_name in os.listdir(domain_dir):
            task_dir = os.path.join(domain_dir, task_name)
            if not os.path.isdir(task_dir):
                continue
            if "sas_plan" not in os.listdir(task_dir):
                continue
            task_file = os.path.join(task_dir, task_name + ".pddl")
            plan_file = os.path.join(task_dir, "sas_plan")
            task_files.append(task_file)
            plan_files.append(plan_file)
        fuzzed_tasks.append((fuzzed_dir, domain_file, task_files, plan_files))

    num_failed = 0
    for t in tqdm(fuzzed_tasks):
        fuzzed_dir, domain_file, task_files, plan_files = t
        try:
            start_time = time.process_time()
            syt = SystemMult(domain_file, task_files, plan_files)
            diagnoser = DiagnoserMult(syt)
            d = diagnoser.diagnosis()
            end_time = time.process_time()
        except Exception as e:
            msg = "Failed: {}".format(task_file)
            logging.error(msg)
            logging.error(traceback.format_exc())
            num_failed += 1
            continue
        diagnosis_time = end_time - start_time

        with open(os.path.join(fuzzed_dir, "fuzz_ops.txt")) as f:
            all_ops = f.readlines()
        num_fuzz_ops = len([op for op in all_ops if op.strip()])

        with open(os.path.join(fuzzed_dir, "diagnosis"), "w") as f:
            for c in d:
                f.write(str(c))
                f.write("\n")
            f.write("time: {}".format(diagnosis_time))
        
        for idx, a in enumerate(syt.systems[0].task.actions):
            for c in d:
                if a.name == c.action_name:
                    syt.systems[0].task.actions[idx] = c.apply(syt.systems[0].task.actions[idx])
        with open(os.path.join(fuzzed_dir, "domain-repaired.pddl"), "w") as f:
            f.write(syt.systems[0].task.domain())
    print("- Num failed: {}".format(num_failed))