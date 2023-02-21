import argparse
import sys


def parse_args():
    argparser = argparse.ArgumentParser()
    subparsers = argparser.add_subparsers(
            dest="name",
            help=("sub-commands for evaluation" 
                  " on different benchmarks"))
    parser_one_to_one = subparsers.add_parser(
            "eval_one_to_one",
            help=("evaluation on instances where one domain"
                  " is paired with one plan"))
    parser_one_to_one.add_argument(
            "--benchmark_dir", required=True,
            help="the directory of the benchmarks")
    parser_one_to_one.add_argument(
            "--err_rates", nargs="+", 
            required=True, type=float,
            help="specify the error rates")
    parser_one_to_mult = subparsers.add_parser(
            "eval_one_to_mult",
            help=("evaluation on instances where one domain"
                  " is paired with multiple plans"))
    parser_one_to_mult.add_argument(
            "--benchmark_dir", required=True,
            help="the directory of the benchmarks")
    parser_one_to_mult.add_argument(
            "--err_rates", nargs="+", 
            required=True, type=float,
            help="specify the error rates")
    

    return argparser.parse_args()


def copy_args_to_module(args):
    module_dict = sys.modules[__name__].__dict__
    for key, value in vars(args).items():
        module_dict[key] = value


def setup():
    args = parse_args()
    copy_args_to_module(args)


setup()