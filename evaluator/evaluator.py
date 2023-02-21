import os
import sys
import subprocess
import logging
import options
from tqdm import tqdm

class Evaluator:
    def __init__(self, err_rate : float, 
                 benchmark_dir : str) -> None:
        logging.basicConfig(
                filename="err.log", 
                level=logging.DEBUG, 
                format="%(asctime)s %(levelname)s %(name)s %(message)s")
        self.logger=logging.getLogger(__name__)
        self._collect_benchmarks(err_rate, benchmark_dir)
    
    def _collect_benchmarks(self, err_rate : float,
                            benchmark_dir : str) -> None:
        raise NotImplementedError
    
    def evaluate(self) -> None:
        cmd = [sys.executable, "../diagnoser.py"]
        for (fuzzed_domain_dir, domain_file, 
                task_files, plan_files) in tqdm(self.tasks):
            subargs = ["--domain", domain_file,
                       "--tasks", task_files,
                       "--plans", plan_files,
                       "--out_diagnosis",
                       fuzzed_domain_dir,
                       "--out_domain",
                       fuzzed_domain_dir,
                       "--evaluation"]
            cmd += subargs
            proc = subprocess.run(cmd, text=True,
                                  capture_output=True)
            if proc.returncode:
                msg = "Failed: {}".format(task_files)
                self.logger.debug(msg)
                self.logger.debug(proc.stdout)
                self.logger.debug(proc.stderr)


class EvaluatorOneToOne(Evaluator):
    def _collect_benchmarks(self, err_rate : float, 
                 benchmark_dir : str) -> None:
        self.tasks = []
        for domain_name in os.listdir(benchmark_dir):
            if domain_name == ".ipynb_checkpoints":
                continue
            domain_dir = os.path.join(benchmark_dir, 
                                      domain_name)
            if not os.path.isdir(domain_dir):
                continue
            for task_name in os.listdir(domain_dir):
                task_dir = os.path.join(domain_dir, 
                                        task_name)
                if not os.path.isdir(task_dir):
                    continue
                if "sas_plan" not in os.listdir(task_dir):
                    continue
                fuzzed_domain_dir = os.path.join(
                        task_dir, "err-rate-{}".format(err_rate))
                task_file = os.path.join(task_dir, 
                                         task_name + ".pddl")
                plan_file = os.path.join(task_dir, 
                                         "sas_plan")
                domain_file = os.path.join(fuzzed_domain_dir, 
                                           "domain.pddl")
                self.tasks.append((fuzzed_domain_dir, domain_file, 
                                  task_file, plan_file))
        

class EvaluatorOneToMult(Evaluator):
    def _collect_benchmarks(self, err_rate : float,
                 benchmark_dir : str) -> None:
        self.tasks = []
        for domain_name in os.listdir(benchmark_dir):
            if domain_name == ".ipynb_checkpoints":
                continue
            domain_dir = os.path.join(benchmark_dir, domain_name)
            if not os.path.isdir(domain_dir):
                continue
            fuzzed_domain_dir = os.path.join(
                    domain_dir, 
                    "err-rate-{}".format(err_rate))
            domain_file = os.path.join(fuzzed_domain_dir, "domain.pddl")
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
            self.tasks.append((fuzzed_domain_dir, domain_file, 
                               task_files, plan_files))
            
if __name__ == "__main__":
    if options.name == "eval_one_to_one":
        print("- Start evaluation on instances where" 
              " one domain is paired with one plan")
        for err_rate in options.err_rates:
            evaluator = EvaluatorOneToOne(
                    err_rate, options.benchmark_dir)
            evaluator.evaluate()
        print("- Done!")
    elif options.name == "eval_one_to_mult":
        print("- Start evaluation on instances where" 
              " one domain is paired with multiple plans")
        for err_rate in options.err_rates:
            evaluator = EvaluatorOneToMult(
                    err_rate, options.benchmark_dir)
            evaluator.evaluate()
        print("- Done!")
    else:
        raise ValueError