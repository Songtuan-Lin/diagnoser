import os
import time
import logging
import resource
import traceback
import options
from memory_profiler import memory_usage
from system import System
from diagnoser import Diagnoser
from tqdm import tqdm

logging.basicConfig(filename="err.log", level=logging.DEBUG, 
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger=logging.getLogger(__name__)

if __name__ == "__main__":
    fuzzed_tasks = []
    for domain_name in os.listdir(options.benchmark_dir):
        if domain_name == ".ipynb_checkpoints":
            continue
        domain_dir = os.path.join(options.benchmark_dir, domain_name)
        if not os.path.isdir(domain_dir):
            continue
        for task_name in os.listdir(domain_dir):
            task_dir = os.path.join(domain_dir, task_name)
            if not os.path.isdir(task_dir):
                continue
            if "sas_plan" not in os.listdir(task_dir):
                continue
            fuzzed_dir = os.path.join(task_dir, "err-rate-{}".format(options.err_rate))
            task_file = os.path.join(task_dir, task_name + ".pddl")
            plan_file = os.path.join(task_dir, "sas_plan")
            domain_file = os.path.join(fuzzed_dir, "domain.pddl")
            fuzzed_tasks.append((fuzzed_dir, domain_file, task_file, plan_file))

    num_failed = 0
    for t in tqdm(fuzzed_tasks):
        fuzzed_dir, domain_file, task_file, plan_file = t
        try:
            start_time = time.process_time()
            syt = System(domain_file, task_file, plan_file)
            diagnoser = Diagnoser(syt)
            d = diagnoser.diagnosis()
            end_time = time.process_time()
            if options.record_mem:
                mem_usage = max(memory_usage(diagnoser.diagnosis, interval=.01))
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
            f.write("time: {}\n".format(diagnosis_time))
            if options.record_mem:
                f.write("memory: {}".format(mem_usage))
            else:
                peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                f.write("memory: {}".format(float(peak/1024)))
        
        for idx, a in enumerate(syt.task.actions):
            for c in d:
                if a.name == c.action_name:
                    syt.task.actions[idx] = c.apply(syt.task.actions[idx])
        with open(os.path.join(fuzzed_dir, "domain-repaired.pddl"), "w") as f:
            f.write(syt.task.domain())
    print("- Num failed: {}".format(num_failed))
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print("- Peak memory usage: {}Mb".format(float(peak/1024)))

