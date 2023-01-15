# Introduction
This is the implementation of the planning domain repair approach described in the paper *Towards Automated Modeling Assistance: An Efficient Approach for Repairing Flawed Planning Domains* accepted by AAAI 2023. This directory contains the implementation together with the benchmark sets on which the emperical evaluation was run and the code for randomly generating flawed domains.

# Running the Domain Repairer

The directory diagnoser_lifted contains the implementation for lifted domains with *negative* preconditions. Notably, the implementation
relies on the PDDL parser which is initially developed in the [Fast-downward planner](https://github.com/aibasel/downward) and then refined in the project [**LAPKT**](https://github.com/LAPKT-dev/LAPKT-public/). Thus, in order to run the implementation, you shall first copy the parser code from [LAPKT](https://github.com/LAPKT-dev/LAPKT-public/) to the directory diagnoser_lifted, which can be done as follows, assuming that you are in the directory containing this README file.

```
git clone https://github.com/LAPKT-dev/LAPKT-public.git
cp -r LAPKT-public/2.0/external/fd diagnoser_lifted/.
```

The domain repairer can then be run by executing the script diagnoser.py in diagnoser_lifted, which takes three command-line arguments: --domain, --task, and --plan. The argument --domain specifies the path to the pddl domain file, --task specifies the path to the pddl task file, and --plan specifies the path to the file containing the input plan. For instance, the below commands run the repairer, assuming that the files domain.pddl, task.pddl, and sas_plan are in the directory diagnoser_lifted.
```
cd diagnoser_lifted
python diagnoser.py --domain domain.pddl --task task.pddl --plan sas_plan 
```
In particular, the format of the plan written in the file sas_plan should align with the output format of the [Fast Downward](https://www.fast-downward.org/) planner.

# Reproducing the Experiment Results
You can reproduce the experiment results reported in the paper by following the instructions below.

## Unzip the Benchmark Sets
In order to reproduce the experiment results, you shall first unzip the benchmark sets. 
Due to the large size of the benchmark sets, they are zipped separately. You can unzip the benchmark sets via the following commands. Note that the commands only work if you place all zipped benchmark set files in the *parent directory* of the current directory:
```
mkdir benchmarks_G1
mkdir benchmarks_G2
unzip -q ../benchmarks_G1_part1.zip -d benchmarks_G1
unzip -q ../benchmarks_G1_part2.zip -d benchmarks_G1
unzip -q ../benchmarks_G2.zip -d benchmarks_G2
```

## Structure of the Benchmark Sets
There are two benchmark sets, $\mathcal{G}_{1}$ and $\mathcal{G}_{2}$. $\mathcal{G}_{1}$ consists of domain repair problem instances where each flawed domain is associated with *one* planning task, and $\mathcal{G}_{2}$ consists of instances where each flawed domain corresponds to *multiple* planning tasks. After unzipping the benchmark sets by following the previous commands, the structure of these two sets will be as follows:
```bash
|-- benchamrks_G1
|   |-- domain_1
|   |   |-- task_1
|   |   |   |-- err-rate-0.1
|   |   |   |   |-- domain.pddl
|   |   |   |   |-- fuzz_ops.txt
|   |   |   |-- err-rate-0.3
|   |   |   |   |-- domain.pddl
|   |   |   |   |-- fuzz_ops.txt
|   |   |   |-- err-rate-0.5
|   |   |   |   |-- domain.pddl
|   |   |   |   |-- fuzz_ops.txt
|   |   |   |-- task_file.pddl
|   |   |   |-- sas_plan
|   |   |-- task_2
|   |   |   |-- ...
|   |   |   |
|   |   |   |-- ...   
│   |-- domain_2
|   |   |-- ...
|   |   |
|   |   |-- ...
|   |
|   |-- ...
```

```
|-- benchamrks_G2
|   |-- domain_1
|   |   |-- err-rate-0.1
|   |   |   |-- domain.pddl
|   |   |   |-- fuzz_ops.txt
|   |   |-- err-rate-0.3
|   |   |   |-- domain.pddl
|   |   |   |-- fuzz_ops.txt
|   |   |-- err-rate-0.5
|   |   |   |-- domain.pddl
|   |   |   |-- fuzz_ops.txt
│   │   |-- task_1
|   |   |   |-- task_file.pddl
|   |   |   |-- sas_plan
|   |   |-- task_2
|   |   |   |-- task_file.pddl
|   |   |   |-- sas_plan   
│   |-- domain_2
|   |   |-- ...
|   |   |
|   |   |-- ...
|   |-- ...
```
In both benchmark sets, a directory err-rate-X (where X is 0.1, 0.3, or 0.5) contains a domain PDDL file of the respective error rate (see the paper for how errors are introduced to the domain model) together with a fuzz_ops.txt file indicating what errors are introduced. In each task directory (in both benchmark sets), the file sas_plan in each directory is the solution plan to the respective planning task found by invoking the planner Fast-downward.

## Reproducing the Results
The empirical evaluation on the benchmark set $\mathcal{G}_{1}$ can be run by executing the script main.py in the directory diagnoser_lifted. In particular, in order to let the evaluation run successfully, you shall have the package **tqdm** in your Python environment, which can be installed via the following command:
```
pip install tqdm
```
The following commands run the main.py script by specifying 
the path to the benchmark set and the instances to be repaired that are of a certain error rate (0.5 in this example). Notebly, the main.py script also requires that the folder **fd** should be corrected copied from [LAPKT](https://github.com/LAPKT-dev/LAPKT-public/).
```
cd diagnoser_lifted
python main.py --benchamrk_dir ../benchmark_G1 --err_rate 0.5
``` 
This command will produce two files, domain_repaired.pddl and diagnosis.txt, in **each** err-rate-0.5 directory in the benchmark set $\mathcal{G}_{1}$.  domain_repaired.pddl is the PDDL file for the repaired domain, and diagnosis.txt contains the found diagnosis together with the runtime for that.

Similarly, the experiment results on the benchmark set $\mathcal{G}_{2}$ can be reproduced by running the script **main_mult.py** with similar arguments. E.g.,
```
cd diagnoser_lifted
python main_mult.py -benchamrk_dir ../benchmark_G2 --err_rate 0.5
```

Further, you could use the code in the (Jupyter) Notebook in each benchmark directory, **collect_data.ipynb**, to collect and plot the runtime information for the empirical evaluation.

# Generate Your Own Benchmark Set of Flawed Domain
The directory **fuzzer** contains the python scripts for generating flawed domains. The scripts **main.py** and **main_neg_prec.py** generate a benchmark set of flawed domains where each flawed domain is associated with one planning task by randomly introducing errors to correct domains without and with negative preconditions, respectively. Both scripts take three positional command line arguments:

+ benchmark_dir: The directory of the correct domains. In our evaluation, we used the [Fast-downward Problem Suite](https://github.com/aibasel/downward-benchmarks).  
+ output_dir: The directory where the flawed domains are produced.
+ err_rate: The error rate introduced to the correct domains (see our main paper for how an error rate is defined).

The scripts also accept the path to the Fast-downward planner executable as an optional argument. If this argument is provided, the scripts will call Fast-downward to find the respective plans as well.

For instance, if you have the Fast-downward Problem Suite in *this* directory, the following command will produce a benchmark set of flawed domains without negative preconditions in the directory **benchmarks_example** where each flawed domain is associated with one planning task and of error rate 0.5.
```
python main.py downward_problem_suite benchmarks_example 0.5
```  

Similarly, the scripts **main_mult.py** and **main_mult_neg_prec.py** will produce a benchmark set where each flawed domain is associated with *multiple* planning tasks and accept the same command line arguments as the previous two. 