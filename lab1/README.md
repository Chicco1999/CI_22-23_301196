# Lab1: set covering

# Model

The problem has been modeled as a tree search, where each node corresponds to a possible set of unique numbers 
contained in the lists that have been chosen for the solution. Each node can be expanded by adding a list to the current
solution, and the cost of such expansion is given by the length of the list.

# Algorithm

The algorithm that has been chosen is a A* type of alghoritm, using as a heuristic function the number of elements that
a given state is missing with respect to the solution. This approach provided optimal results for the smallest values
of N (5,10,20). However, starting from N = 100 the complexity made it impossible to obtain a result in a reasonable time.
The best results, as a compromise between time and quality of the solution, have been obtained by using a greedy best-first approach, using the pre-define heuristics as the priority function

# Results

N = 5: Found a solution of weight 5 after visiting 21 nodes
N = 10: Found a solution of weight 10 after visiting 738 nodes
N = 20: Found a solution of weight 23 after visiting 15,258 nodes
N = 100: Found a solution of weight 173 after visiting 1,603 nodes
N = 500: Found a solution of weight 1,304 after visiting 10,778 nodes
N = 1000: Found a solution of weight 2,893 after visiting 24,238 nodes
