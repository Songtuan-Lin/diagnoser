# Introduction
This is the implementation of the planning domain repair approach described in the paper *Towards Automated Modeling Assistance: An Efficient Approach for Repairing Flawed Planning Domains* accepted by AAAI 2023. The program takes as input a (potentially flawed) PDDL domain file, a list of PDDL task files, and a list of plan files containing plans each of which is supposed to be a solution to the respective given planning task (but it might not be the case due to the flaws in the given domain) and outputs a repaired domain in which every given plan is guaranteed to be a solution.

The implementation relies on the PDDL parser (in the directory fd) that is copied from the project [LAPKT](https://github.com/LAPKT-dev/LAPKT-public/). 

# Run the Domain Repairer

### Requirement

The program is written in python. Thus, you must have Python installed in your device in order to run the code.

### Command

You can use the following command to run the domain repairer, assuming that you are in the directory containing this README file. 

```
python diagnoser.py --domain domain.pddl --tasks task-1.pddl ... task-n.pddl --plans planfile-1 ... planfile-n
```

Note that the plan contained in each file must be of the format that is identical to the output format of the [Fast-downward](https://github.com/aibasel/downward) planner, shown as follows.

```
(action-name-1 para-1 para-2 ... para-n)
                    .
                    .
                    .
(action-name-k para-1 para-2 ... para-n)
```

The repairer will output a repaired domain in a PDDL file if you provide a path to the argument `--out_domain`. E.g.,
```
python diagnoser.py --domain domain.pddl --tasks task-1.pddl ... task-n.pddl --plans planfile-1 ... planfile-n --out_domain output_path
```
The output PDDL domain file will be on the path: output_path/domain-repaired.pddl (Please **do not** give the PDDL file name as a part of the parameter!). Similarly, the repairer will write found repairs to a file called *diagnosis* if a path is given to the argument `--out_diagnosis` on which the file will be produced. You can use the command
```
python diagnoser.py --help
```
to check all arguments accepted by the program.

# Cite
```
@InProceedings{Lin2023RepairingClassicalModels,
  author     = {Songtuan Lin and Alban Grastien and Pascal Bercher},
  booktitle  = {Proceedings of the 37th AAAI Conference on Artificial Intelligence (AAAI 2023)},
  title      = {Towards Automated Modeling Assistance: An Efficient Approach for Repairing Flawed Planning Domains},
  year       = {2023},
  publisher  = {AAAI Press},
}
```
