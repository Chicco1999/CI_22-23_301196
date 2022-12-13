import logging
from collections import namedtuple
import random
from typing import Callable
from copy import deepcopy
from itertools import accumulate
from operator import xor

NUM_MATCHES = 50
NIM_SIZE = 6

Nimply = namedtuple("Nimply", "row, num_objects")
class Nim:
    def __init__(self, num_rows: int, k: int = None) -> None:
        self._rows = [i * 2 + 1 for i in range(num_rows)]
        self._k = k

    def __bool__(self):
        return sum(self._rows) > 0

    def __str__(self):
        return "<" + " ".join(str(_) for _ in self._rows) + ">"

    @property
    def rows(self) -> tuple:
        return tuple(self._rows)

    @property
    def k(self) -> int:
        return self._k

    def nimming(self, ply: Nimply) -> None:
        row, num_objects = ply
        assert self._rows[row] >= num_objects
        assert self._k is None or num_objects <= self._k
        self._rows[row] -= num_objects


# random strategy

def pure_random(state: Nim) -> Nimply:
    row = random.choice([r for r, c in enumerate(state.rows) if c > 0])
    num_objects = random.randint(1, state.rows[row])
    return Nimply(row, num_objects)

def nim_sum(state: Nim) -> int:
    *_, result = accumulate(state.rows, xor)
    return result

def cook_status(state: Nim) -> dict:
    cooked = dict()
    cooked["active_rows"] = [x[0] for x in filter(lambda r: r[1] > 0, enumerate(state.rows))]
    cooked["possible_moves"] = [
        (r, o) for r, c in enumerate(state.rows) for o in range(1, c + 1) if state.k is None or o <= state.k
    ]
    cooked["nim_sum"] = nim_sum(state)
    return cooked

def cook_status_optimal(state: Nim) -> dict:
    cooked = dict()
    cooked["possible_moves"] = [
        (r, o) for r, c in enumerate(state.rows) for o in range(1, c + 1) if state.k is None or o <= state.k
    ]
    
    brute_force = list()
    for m in cooked["possible_moves"]:
        tmp = deepcopy(state)
        tmp.nimming(m)
        brute_force.append((m, nim_sum(tmp)))
    cooked["brute_force"] = brute_force

    return cooked

def eval_state(data):
    if len(data["active_rows"]) == 0 or data["nim_sum"] == 0:
        return -1
    elif len(data["active_rows"]) == 1:
        return 1
    else:
        return 0

actions = dict()
knownStates = dict()


def nextState(state: Nim,action) -> Nim: #Generate the following state without modifying the pre-existing one
    newState = deepcopy(state)
    newState.nimming(Nimply(action[0],action[1]))
    return newState

def MMagent(state: Nim) -> Nimply:  #Wrapper for the recursive agent

    ply = minMax(state)
    return Nimply(ply[0][0],ply[0][1])

def minMax(state: Nim) -> tuple:
    if state.rows in knownStates:
        return actions[state.rows], knownStates[state.rows]
    data = cook_status(state)
    val = eval_state(data)
    if val != 0 or not data["possible_moves"]:
        if val == 1:
            return (data["active_rows"][0],state.rows[data["active_rows"][0]]),val
        else:
            return (data["active_rows"][0],1),val   #This move is meaningless anyway
    evaluations = list()
    bound = 1
    for a in data["possible_moves"]:
        _ , val = minMax(nextState(state,a))
        if val > bound:
            #print(f"pruning {len(data['possible_moves'][data['possible_moves'].index(a):])} states")
            break
        elif val < bound:
            bound = val
        evaluations.append((a,-val))
    ply = max(evaluations,key=lambda k: k[1])
    actions[state.rows] = ply[0]
    knownStates[state.rows] = ply[1]
    return ply

def nim_sum(state: Nim) -> int:
    *_, result = accumulate(state.rows, xor)
    return result

def optimal_startegy(state: Nim) -> Nimply:
    data = cook_status_optimal(state)
    return next((bf for bf in data["brute_force"] if bf[1] == 0), random.choice(data["brute_force"]))[0]


def evaluate(strategy1: Callable, strategy2=pure_random) -> float:
    opponent = (strategy1, strategy2)
    won = 0

    for m in range(NUM_MATCHES):
        nim = Nim(NIM_SIZE)
        player = 0
        while nim:
            ply = opponent[player](nim)
            nim.nimming(ply)
            player = 1 - player
        if player == 1:
            won += 1

    opponent = (strategy2,strategy1)

    for m in range(NUM_MATCHES):
        nim = Nim(NIM_SIZE)
        player = 0
        while nim:
            ply = opponent[player](nim)
            nim.nimming(ply)
            player = 1 - player
        if player == 0:
            won += 1

    return won / (2*NUM_MATCHES)

nim = Nim(NIM_SIZE)
wr = evaluate(MMagent)
print(f"The agent has a {wr} win ratio out of {2*NUM_MATCHES} games against a random agent")
wr = evaluate(MMagent,optimal_startegy)
print(f"The agent has a {wr} win ratio out of {2*NUM_MATCHES} games against a perfect agent")

