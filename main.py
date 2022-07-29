from system import System
from diagnoser import Diagnoser

if __name__ == "__main__":
    syt = System("/home/garrick/codes/fuzzer/domain.pddl", "/home/garrick/projects/diagnosis/p18.pddl", "/home/garrick/projects/diagnosis/sas_plan")
    diagnoser = Diagnoser(syt)
    d = diagnoser.diagnosis()
    for c in d:
        print(c)