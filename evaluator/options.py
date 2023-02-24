import argparse
import sys


def parse_args():
    argparser = argparse.ArgumentParser()
    group = argparser.add_mutually_exclusive_group(
            required=True)
    group.add_argument(
            "--single", action="store_true",
            default=False,
            help=("evaluate benchmarks where "
                  "one domain is paried with "
                  "one planning task"))
    group.add_argument(
            "--multiple", action="store_true",
            default=False,
            help=("evaluate benchmarks where "
                  "one domain is paried with "
                  "multiple planning tasks"))
    argparser.add_argument(
                "-n", "--num_cpus", type=int,
                help="number of CPUs to be used")
    argparser.add_argument(
            "--benchmark_dir", required=True,
            help="the directory of the benchmarks")
    argparser.add_argument(
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