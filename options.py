import argparse
import sys


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--benchmark_dir", type=str, help="directory of the benchmark set")
    argparser.add_argument(
        "--err_rate", type=float, help="error rate")
    argparser.add_argument(
        "--domain", help="path to domain pddl file")
    argparser.add_argument(
        "--task", help="path to task pddl file")
    argparser.add_argument(
        "--plan", help="path to plan file")
    argparser.add_argument(
        "--out_dir", help="path to write repaired domain pddl file"
    )
    argparser.add_argument(
        "--grounded", action="store_true", help="diagnosis in the grounded setting")
    return argparser.parse_args()


def copy_args_to_module(args):
    module_dict = sys.modules[__name__].__dict__
    for key, value in vars(args).items():
        module_dict[key] = value


def setup():
    args = parse_args()
    copy_args_to_module(args)


setup()
