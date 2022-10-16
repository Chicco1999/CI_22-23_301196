import random
from turtle import st
def problem(N, seed=None):
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]
import logging

from gx_utils import *

logging.getLogger().setLevel(logging.INFO)

from typing import Callable

def search(
    initial_state: tuple,
    goal_test: Callable,
    parent_state: dict,
    state_cost: dict,
    priority_function: Callable,
    unit_cost: Callable,
    beam = 0
):
    frontier = PriorityQueue()
    parent_state.clear()
    state_cost.clear()

    state = initial_state
    parent_state[state] = None
    state_cost[state] = 0
    

    while state is not None and not goal_test(state):
        count = 0
        for a in possible_actions(state):
            if beam:
                count +=1
                if count >= beam:
                    break
            new_state = result(state, a)
            cost = unit_cost(a)
            if new_state not in state_cost and new_state not in frontier:
                parent_state[new_state] = state
                state_cost[new_state] = state_cost[state] + cost
                frontier.push(new_state, p=priority_function(new_state))
                logging.debug(f"Added new node to frontier (cost={state_cost[new_state]})")
            elif new_state in frontier and state_cost[new_state] > state_cost[state] + cost:
                old_cost = state_cost[new_state]
                parent_state[new_state] = state
                state_cost[new_state] = state_cost[state] + cost
                logging.debug(f"Updated node cost in frontier: {old_cost} -> {state_cost[new_state]}")
        if frontier:
            state = frontier.pop()
        else:
            state = None

    path = list()
    s = state
    while s:
        path.append(list(s))
        s = parent_state[s]
    logging.info(f"Found a solution of weight {state_cost[state]:,}; visited {len(state_cost):,} states")
    return list(reversed(path))

def goal_test(state):
    return len(state) == len(goal)

def possible_actions(state: tuple):
    return (l for l in all_lists if not set(l) < set(state))

def result(state, action):
    return tuple(set(state).union(set(action)))

def h(state):
    return len(goal) - len(state)

for N in [5, 10, 20]:
    goal = tuple(range(N))
    parent_state = dict()
    state_cost = dict()
    all_lists = problem(N, seed=42)

    final = search(
        tuple(),
        goal_test=goal_test,
        parent_state=parent_state,
        state_cost=state_cost,
        priority_function=lambda s: state_cost[s] + h(s),
        unit_cost=lambda a: len(a),
    )
for N in [100, 500, 1000]:
    goal = tuple(range(N))
    parent_state = dict()
    state_cost = dict()
    all_lists = problem(N, seed=42)

    final = search(
        tuple(),
        goal_test=goal_test,
        parent_state=parent_state,
        state_cost=state_cost,
        priority_function=lambda s: h(s),
        unit_cost=lambda a: len(a),
    )