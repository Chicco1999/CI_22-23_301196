import logging
from collections import namedtuple
import random
from typing import Callable
from copy import deepcopy
from itertools import accumulate
from operator import xor
from math import ceil
import numpy as np

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

def expert_strategy(state: Nim) -> Nimply:
    ACTIVE_ROWS_TH1 = 3 #Threshold for rule about row selection
    ROW_CHOICE1 = 7  #Nth shortest row chosen for selection if rule 1 is triggered
    ROW_CHOICE2 = 5 #Nth shortest row chosen for selection if rule 1 is not triggered
    ROW_LEN_TH = 5 #Threshold for rule about n° items to remove
    ACTIVE_ROWS_TH2 = 2 # 2nd threshold for rule about n° items to remove
    #All the following are fractions of a row to remove according to prevoius conditions
    ITEM_CHOICE1 = 0.2  
    ITEM_CHOICE2 = 0.4
    ITEM_CHOICE3 = 0.9
    ITEM_CHOICE4 = 0.7
    data = cook_status(state)
    row_choices = set(data["active_rows"])   #Phase 1: select a row to remove items from

    if len(data["active_rows"]) == 1:  #Hardcoded win condition, win if you can
        row_choices = data["active_rows"][0]
        ply = Nimply(row_choices,state.rows[row_choices])
        return ply

    if len(data["active_rows"]) < ACTIVE_ROWS_TH1:
        row_choices = sorted(data["active_rows"],key=lambda r: state.rows[r])[ROW_CHOICE1 % len(data["active_rows"])] #Normalization of the parameter to the actual list of active rows
    else:
        row_choices = sorted(data["active_rows"],key=lambda r: state.rows[r])[ROW_CHOICE2 % len(data["active_rows"])]

    if state.rows[row_choices] > ROW_LEN_TH:
        if len(data["active_rows"]) < ACTIVE_ROWS_TH2:
            #The number of items to remove is calculated as a fraction of the number of items in the row, rounded up to the closest integer
            assert(ceil(state.rows[row_choices] * ITEM_CHOICE1)> 0 and ceil(state.rows[row_choices] * ITEM_CHOICE1) <= state.rows[row_choices])
            ply = Nimply(row_choices,ceil(state.rows[row_choices] * ITEM_CHOICE1))
        else:
            assert(ceil(state.rows[row_choices] * ITEM_CHOICE2)> 0 and ceil(state.rows[row_choices] * ITEM_CHOICE2) <= state.rows[row_choices])
            ply = Nimply(row_choices,ceil(state.rows[row_choices] * ITEM_CHOICE2))
    else:
        if len(data["active_rows"]) < ACTIVE_ROWS_TH2:
            assert(ceil(state.rows[row_choices] * ITEM_CHOICE3)> 0 and ceil(state.rows[row_choices] * ITEM_CHOICE3) <= state.rows[row_choices])
            ply = Nimply(row_choices,ceil(state.rows[row_choices] * ITEM_CHOICE3))
        else:
            assert(ceil(state.rows[row_choices] * ITEM_CHOICE4) > 0 and ceil(state.rows[row_choices] * ITEM_CHOICE4) <= state.rows[row_choices])
            ply = Nimply(row_choices,ceil(state.rows[row_choices] * ITEM_CHOICE4))

    return ply


def cook_status(state: Nim) -> dict:
    cooked = dict()
    cooked["active_rows"] = [x[0] for x in filter(lambda r: r[1] > 0, enumerate(state.rows))]
    return cooked

# Function specific for an agent applying the nim sum strategy
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

#Optimal startegy, the first to move always wins

def nim_sum(state: Nim) -> int:
    *_, result = accumulate(state.rows, xor)
    return result

def optimal_startegy(state: Nim) -> Nimply:
    data = cook_status_optimal(state)
    return next((bf for bf in data["brute_force"] if bf[1] == 0), random.choice(data["brute_force"]))[0]

#Function to create a strategy starting from a genome

def make_strategy(genome: dict) -> Callable:
    def evolvable(state: Nim) -> Nimply:
        data = cook_status(state)
        row_choices = set(data["active_rows"])   

        if len(data["active_rows"]) == 1: 
            row_choices = data["active_rows"][0]
            ply = Nimply(row_choices,state.rows[row_choices])
            return ply

        if len(data["active_rows"]) < genome["active_rows_th1"]:
            row_choices = sorted(data["active_rows"],key=lambda r: state.rows[r])[genome["row_choice1"] % len(data["active_rows"])]
        else:
            row_choices = sorted(data["active_rows"],key=lambda r: state.rows[r])[genome["row_choice2"] % len(data["active_rows"])]

        if state.rows[row_choices] > genome["row_len_th"]:
            if len(data["active_rows"]) < genome["active_rows_th2"]:
                assert(ceil(state.rows[row_choices] * genome["item_choice1"])> 0 and ceil(state.rows[row_choices] * genome["item_choice1"]) <= state.rows[row_choices])
                ply = Nimply(row_choices,ceil(state.rows[row_choices] * genome["item_choice1"]))
            else:
                assert(ceil(state.rows[row_choices] * genome["item_choice1"])> 0 and ceil(state.rows[row_choices] * genome["item_choice2"]) <= state.rows[row_choices])
                ply = Nimply(row_choices,ceil(state.rows[row_choices] * genome["item_choice2"]))
        else:
            if len(data["active_rows"]) < genome["active_rows_th2"]:
                assert(ceil(state.rows[row_choices] * genome["item_choice1"])> 0 and ceil(state.rows[row_choices] * genome["item_choice3"]) <= state.rows[row_choices])
                ply = Nimply(row_choices,ceil(state.rows[row_choices] * genome["item_choice3"]))
            else:
                assert(ceil(state.rows[row_choices] * genome["item_choice1"]) > 0 and ceil(state.rows[row_choices] * genome["item_choice4"]) <= state.rows[row_choices])
                ply = Nimply(row_choices,ceil(state.rows[row_choices] * genome["item_choice4"]))

        return ply

    return evolvable

def init_population(size: int):

    #Initialize the population for the evolution process, set up the values of each dictionaries and give initial values for the fitness
    population = [[dict(),0,0] for _ in range(size)]
    for ind in population:
        ind[0] = dict()
        ind[0]["active_rows_th1"] = random.randint(1,NIM_SIZE)
        ind[0]["active_rows_th2"] = random.randint(1,NIM_SIZE)
        ind[0]["row_choice1"] = random.randint(1,NIM_SIZE)
        ind[0]["row_choice2"] = random.randint(1,NIM_SIZE)
        ind[0]["row_len_th"] = random.randint(1,2 * NIM_SIZE + 1)
        ind[0]["item_choice1"] = random.choice(np.arange(0.1,1,0.1))
        ind[0]["item_choice2"] = random.choice(np.arange(0.1,1,0.1))
        ind[0]["item_choice3"] = random.choice(np.arange(0.1,1,0.1))
        ind[0]["item_choice4"] = random.choice(np.arange(0.1,1,0.1))
        ind[1] = evaluate(make_strategy(ind[0]))
        ind[2] = evaluate(make_strategy(ind[0]))
    return population

def mutate(genome: dict) -> dict:
    mutated = deepcopy(genome)
    mutKey = random.choice(list(mutated.keys()))   #Mutate one random value in the genome
    #The mutation is different depending on the gene chosen
    if mutKey in ["active_rows_th1","active_rows_th2","row_choice1","row_choice2"]: 
        #Integer genes are altered by 1
        mutated[mutKey] = (mutated[mutKey] +  random.choice([-1,1])) % NIM_SIZE #Normalize to the number of rows
    elif mutKey == "row_len_th":
        mutated[mutKey] = (mutated[mutKey] +  random.choice([-1,1])) % (2 * NIM_SIZE + 1) #Normalize to the highest number of items in a single row
    else:   
            #Float genes are altered by 0.1
            mutated[mutKey] = (mutated[mutKey] +  random.choice([-0.1,0.1]))
            #Handling of mutations that lead to unfeasible solutions
            if mutated[mutKey] < 0.1:
                mutated[mutKey] = 0.1
            elif mutated[mutKey] > 1:
                mutated[mutKey] = 1
    return mutated

#Random cut crossover
def crossover(genome1: dict, genome2: dict):
    cross = dict()
    cut = random.randint(0,8)
    cross.update(list(genome1.items())[:cut])
    cross.update(list(genome2.items())[cut:])
    return cross

def evolution():

    POP_SIZE = 40
    N_GENS = 50

    population = init_population(POP_SIZE)
    best = sorted(population,key= lambda i: i[1],reverse=True)[0]  #Pick the initial best
    for _ in range(N_GENS):
        print(f"generation {_}")
        offspring = list()
        for ind in population:
            if random.random() < 0.4:
                mutated = mutate(ind[0])
                offspring.append([mutated,evaluate(make_strategy(mutated)),evaluate(make_strategy(mutated),make_strategy(best[0]))])
            ind[1] = evaluate(make_strategy(ind[0]))
            ind[2] = evaluate(make_strategy(ind[0]),make_strategy(best[0]))
        if random.random() < 0.7:
            parent1 = tournament(population)
            parent2 = tournament(population)
            child = crossover(parent1[0],parent2[0])
            offspring.append([child,evaluate(make_strategy(child)),evaluate(make_strategy(child),make_strategy(best[0]))])
        population += offspring
        population = sorted(population,key= lambda i: i[1],reverse=True)[:POP_SIZE]
        if population[0][1] > best[1] and population[0][2] > 0.5:
            best = deepcopy(population[0])
            print(f"New best at generation {_} with genome {best[0]} and winrate {best[1]} against random and {best[2]} against the previous best agent")
    print(f"Final result with genome {best[0]} and winrate {best[2]} against the previous best and {best[1]} against the random strategy")
    return best

#Tournament selection for crossover parents
def tournament(population):
    competitors = random.choices(population,k=5)
    return max(competitors,key=lambda c: c[1])

#Function to evaluate policies, agents play both first and second

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

logging.getLogger().setLevel(logging.DEBUG)

#Example match

def match(player1,player2):

    strategy = (player1, player2)

    nim = Nim(11)
    logging.debug(f"status: Initial board  -> {nim}")
    player = 0
    while nim:
        ply = strategy[player](nim)
        nim.nimming(ply)
        logging.debug(f"status: After player {player} -> {nim}")
        player = 1 - player
    winner = 1 - player
    logging.info(f"status: Player {winner} won!")

NUM_MATCHES = 50
NIM_SIZE = 10
wr = evaluate(expert_strategy,pure_random)
print(f"The expert agent has a win rate of {wr} against a pure random strategy")
evolution()

