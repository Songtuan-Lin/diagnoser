from queue import PriorityQueue

from typing import FrozenSet, List, Set
from dataclasses import dataclass

def hits(set: FrozenSet[int], list: List[int]):
    for e in list:
        if e in set:
            return True
    return False

@dataclass
class HittingObject(): 
    weight: float
    set: FrozenSet[int]
    forbiddens: Set[int] # objects that are not allowed to be chosen
    bc: int
    cc: int
    id: int # used to break ties

    def __lt__(self, other):
        # want weight to be as low as possible
        if other.weight > self.weight:
            return True
        if other.weight < self.weight:
            return False
        # want bc as high as possible
        if other.bc < self.bc:
            return True
        if other.bc > self.bc:
            return False
        # want cc as high as possible
        if other.cc < self.bc:
            return True
        if other.cc > self.bc:
            return False
        return other.id > self.id

    def forbid(self, forbs: List[int]) -> None:
        for f in forbs:
            self.forbiddens.add(f)

class Hitter:
    def __init__(self):
        self._queue = PriorityQueue() # Will contain the HitterObjects
        self._nb_objects = -1
        self._queue.put(self.create_object(None,None))
        self._basic_conflicts = []
        self._complex_conflicts = []
        self._weights = []

    def create_object(self, ho: HittingObject, new_element: int):
        if ho == None:
            w = 0
            new_set = set()
            forbiddens = set()
            bc = 0
            cc = 0
        else:
            w = ho.weight + self.weight(new_element)
            new_set = { e for e in ho.set }
            new_set.add(new_element)
            forbiddens = { e for e in ho.forbiddens }
            bc = ho.bc
            cc = 0

        self._nb_objects += 1
        return HittingObject(weight=w, 
            set=frozenset(new_set), 
            forbiddens=forbiddens,
            bc=bc, 
            cc=cc, 
            id=self._nb_objects, 
        )

    def set_weights(self, weights: List[float]) -> None:
        '''
        Sets the weights of the elements.  
        weights is an array of float.  
        The first element, i.e., number 1, is at array position 1, 
        i.e., the second float of the array;
        in other words, weights[0] gets ignored.
        By default, i.e., if an element is greater than or equal to the length of the list, 
        its value is 1.
        If you modify the weights during the algorithm, 
        there is no guarantee that the best solutions will be returned;
        the main exception is if this methods refines the list of weights, 
        i.e., if you send a longer array with the same values.
        Otherwise, consider using reset_weights instead.
        '''
        self._weights = weights

    def reset_weights(self, weights: List[float]) -> None:
        objects = []
        while not self._queue.empty():
            objects.append(self._queue.get())
        self._weights = weights
        for obj in objects:
            w = 0
            for e in obj.set:
                w += self.weight(e)
            obj.weight = w
            self._queue.put(obj)

    def weight(self, e: int) -> float:
        '''
          Returns the weight of element e.  Default value is 1.
        '''
        if e < len(self._weights):
            return self._weights[e]
        return 1

    def top(self) -> Set[int]:
        '''
          Returns the top element in this hitter.
          The element is *not* removed from the queue.
        '''
        while True:
            obj: HittingObject = self._queue.get()

            while obj.bc < len(self._basic_conflicts): # Deal with all basic conflicts
                conflict = self._basic_conflicts[obj.bc]
                if hits(obj.set, conflict):
                    # already hits this conflict
                    obj.bc += 1
                    continue
                # needs to hit the conflict
                forbs = []
                for e in conflict:
                    if e not in obj.forbiddens:
                        new_object = self.create_object( obj,e )
                        new_object.forbid(forbs)
                        self._queue.put(new_object)
                    forbs.append(e)
                break
                
            if obj.bc != len(self._basic_conflicts):
                continue

            # Dealing with non-basic conflicts
            while obj.cc < len(self._complex_conflicts):
                conflict = self._complex_conflicts[obj.cc]
                applicable = True
                for e in conflict:
                    if e > 0:
                        continue
                    if -e not in obj.set:
                        applicable = False
                        break
                if not applicable:
                    obj.cc += 1
                    continue
                # Need to hit the conflict
                forbs = []
                for e in conflict:
                    if e < 0:
                        continue
                    if e not in obj.forbiddens:
                        new_object = self.create_object( obj,e )
                        new_object.forbid(forbs)
                        self._queue.put(new_object)
                    forbs.append(e)
                break
            
            if obj.cc == len(self._complex_conflicts):
                self._queue.put(obj)
                return obj.set

        return None

    def add_conflict(self, conflict: List[int]) -> None:
        for e in conflict:
            if e < 0:
                self._complex_conflicts.append(conflict)
                return
        self._basic_conflicts.append(conflict)

    def DEBUG_PRINT(self):
        while not self._queue.empty():
            e = self._queue.get()
            print(e)
        print(self._sets)     


if __name__ == '__main__':

    h = Hitter()
    h.set_weights([None, 8, 1, 8, 2, 8, 8, 2, 2, 2, 2])
    print(h.top())
    #print(h)

    h.add_conflict([1,2,3])
    print(h.top())
    #print(h)

    h.add_conflict([2,5,6])
    print(h.top())
    #print(h)

    h.add_conflict([1,5,6])
    print(h.top())
    #print(h)

    h.add_conflict([3,6])
    print(h.top())
    #print(h)

    h.add_conflict([3,5])
    print(h.top())

    h.add_conflict([-3,-6,5,2])
    print(h.top())

    h.add_conflict([-3,-5,2])
    print(h.top())
