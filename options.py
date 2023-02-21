import argparse
import sys


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
            "--domain", required=True,
            help="path to the domain pddl file")
    argparser.add_argument(
            "--tasks", nargs="+", required=True,
            help="path to the task pddl files")
    argparser.add_argument(
            "--plans", nargs="+", required=True,
            help="path to the plan files")
    argparser.add_argument(
            "--out_diagnosis", type=str,
            help="file for writting the diagnosis")
    argparser.add_argument(
            "--out_domain", type=str,
            help="file for writting the repaired domain")
    argparser.add_argument(
            "--evaluation", action="store_true", default=False, 
            help="run the diagnoser for evaluation")
    argparser.add_argument(
            "--print", action="store_true", default=False,
            help="print the found diagnosis")
    return argparser.parse_args()


def copy_args_to_module(args):
    module_dict = sys.modules[__name__].__dict__
    for key, value in vars(args).items():
        module_dict[key] = value


def setup():
    args = parse_args()
    copy_args_to_module(args)


setup()
