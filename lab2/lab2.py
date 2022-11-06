import random
import math
import numpy as np
from turtle import st
def problem(N, seed=None):
    random.seed(seed)
    return np.array([
        tuple(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ])
import logging

all_lists = None

def goal_test(s,N):
    covered = set()
    for l in s:
        covered.update(set(all_lists[l]))
    return N == len(covered)

class fitness:
    def __init__(self,gen):
        covered = set()
        weight = 0
        for l in gen:
            weight += len(all_lists[l])
            covered.update(set(all_lists[l]))
        self.weight = weight
        self.covered = len(covered)

    def __eq__(self,other):
        if self.covered == other.covered and self.weight == other.weight:
            return True
        return False

    def __lt__(self,other):
        if self.covered == other.covered:
            return self.weight > other.weight
        return self.covered < other.covered

    def __le__(self,other):
        if self.covered == other.covered:
            return self.weight >= other.weight
        return self.covered <= other.covered

    def __gt__(self,other):
        if self.covered == other.covered:
            return self.weight < other.weight
        return self.covered > other.covered

    def __ge__(self,other):
        if self.covered == other.covered:
            return self.weight <= other.weight
        return self.covered >= other.covered

def tournament(pop,tournament_size=2):
    return max(random.choices(pop,k=tournament_size),key=lambda i: fitness(i))

def crossover(g1,g2):
    s1 = set(g1)
    s2 = set(g2)
    i = s1.intersection(s2)
    if len(i):
        off = np.array([i])
    off = np.concatenate([g1[:g1.size//2+1],g2[g2.size//2:]])
    return off

def mutate(ind):
    while True:
        new_list = random.choice(range(len(all_lists)))
        if new_list not in ind:
            break
        ind[random.randrange(0,len(ind))] = new_list
    return ind

def evolution(N,pop_size,off_size,generations):
    global all_lists
    all_lists = problem(N,seed=42)
    population = list(np.array([_]) for _ in range(all_lists.size))
    best = max(population,key = lambda i: fitness(i))
    for g in range(generations):
        #print(f"generation={g:,}")
        offspring = list()
        for i in range(off_size):
            p1 = tournament(population,2 + N//50)
            p2 = tournament(population,2 + N//50)
            o = crossover(p1,p2)
            if random.random() < 0.2:
                o = mutate(o)
            offspring.append(o)
        population = offspring
        gen_best = max(population,key = lambda i:fitness(i))
        if fitness(gen_best) > fitness(best):
            best = gen_best
            #print(f"new best candidate with w={sum(len(all_lists[_])for _ in best):,} in generation={g:,}")
    print(f"best candidate with w={sum(len(all_lists[_])for _ in best):,}")
    print(list(all_lists[_] for _ in best))

for N in [5,10,20,100,500,1000]:
    evolution(N,500,500,100)
