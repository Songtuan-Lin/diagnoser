import argparse
import sys


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--benchmark_dir", type=str, help="Directory of the benchmark set")
    argparser.add_argument(
        "--err_rate", type=float, help="Error rate")
    argparser.add_argument(
        "--domain", help="path to domain pddl file")
    argparser.add_argument(
        "--task", help="path to task pddl file")
    argparser.add_argument(
        "--plan", help="path to plan file")
    argparser.add_argument(
        "-m", "--modify", action="store_true", help="randomly modify model", dest="modify")
    argparser.add_argument(
        "-n", "--num", help="number of modifications", dest="num", default=15, type=int)
    return argparser.parse_args()


def copy_args_to_module(args):
    module_dict = sys.modules[__name__].__dict__
    for key, value in vars(args).items():
        module_dict[key] = value


def setup():
    args = parse_args()
    copy_args_to_module(args)


setup()
