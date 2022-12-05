# Lab3: Nim

The goal of this lab is creating agent able to play the game of Nim using different strategies

## The game

The game starts with a board composed on a certain number or rows, each containing an od number of items. One at a time, each player selects one row and removes at least one item from it. The winner is the player that is able to take the last item from the board.

## Evaluation

The evaluation of agents is done with the **evaluate** function, which takes as areguments at most two agents (the second agents is set to a pure random agent by default) and has them compete in a series of matches (**NUM_MATCHES**, set to **50** in this case). Midway through the number of games to play, the agents are switched and the final result is the overall win rate of the agent that needs to be evaluated.

## Strategy 1: expert system

The first strategy implemented is a system that is able to play using hardcoded rules. In this specific case, the agent's actions depend on 9 parameters:

**ACTIVE_ROWS_TH1**,**ACTIVE_ROWS_TH2**,**ROW_CHOICE1**,**ROW_CHOICE2**,**ROW_LEN_TH**,**ITEM_CHOICE1**,**ITEM_CHOICE2**,**ITEM_CHOICE3**,**ITEM_CHOICE4**

The **_TH** parameters are thresholds that trigger different courses of action according to the board condition, while the **_CHOICE** parameters are related to the decisions of the agent.

The **ROW** choices are expressed in the form of n-th shortest active row to pick items from, while the **ITEM** choices are expressed as fractions of items to take from a specific row (with a granularity of 0.1)

There is also an extra rule, the **win condition**: if only **1** active row is left, take all items from it to win the game

With the following configuration:

    ACTIVE_ROWS_TH1 = 3 
    ROW_CHOICE1 = 7 
    ROW_CHOICE2 = 5 
    ROW_LEN_TH = 5 
    ACTIVE_ROWS_TH2 = 2 
    ITEM_CHOICE1 = 0.2  
    ITEM_CHOICE2 = 0.4
    ITEM_CHOICE3 = 0.9
    ITEM_CHOICE4 = 0.7
The expert system, put against a pure random agent, has on average a **60%** win rate

## Strategy 2: evolved rules with GA

The second agent is obtained by putting the parameters that regulate the expert system into a GA in order to obtain better parameters.

### Individual

The individuals are represented by a dictionary, with an entry for each of the 9 previously defined parameters, and 2 values that represent the fitness of the individual given by the win rate against the **pure random** agent for **both** parameters.

While the parametrized rules are evolved together with the GA, the **win condition** is still hardcoded into each individual. This has been done in the hope of finding better solutions at the end of the evoultion process 

### Fitness function

The fitness is represented by 2 values, the first being the win rate against a **pure random agent** and the other being the win rate agains the **previous best solution** found by the algorithm.

The current best solution is replaced if the new agent has a **greater or equal** win rate agains the random agent **AND** a **higher than 50%** win rate agains the previous best.

### Initialization

The initialization is done by generating **POP_SIZE** individuals with random genes and fitness dictated by the win rate agains the pure random agent 

### Genetic operators

#### **Mutation**

The mutation function is applied with a certain probability to each individual of the population. It selects a **random gene** and it applies a different muation step according to the type of the selected gene: <br>
**Integer** genes are randomly altered by **1** while **float** genes are randomly altered by **0.1**

The mutated gene also goes through some **normalization** to avoid unfeasible solutions.<br>
Specifically, **row choice related** integer gens are normalized to the maximum number of rows, the **row lenght** related gene is normalized to the maximum number of items that can be present in a row and **float** genes, if they go beyond the boundaries of **0.1** and **1**, they are set to the nearest boundary.

#### **Crossover**

Crossover is performed after mutation with a certain rate. It selects 2 parents with a **tournament selection** process and combines their genes with a **random cut**.

### Results

After running the genetic algorithm with the following parameters

    POP_SIZE = 40
    N_GENS = 50
    MUTATION_RATE = 0.4
    CROSSOVER_RATE = 0.3

The best candidate had the following parameters

    ACTIVE_ROWS_TH1 = 5
    ACTIVE_ROWS_TH2 = 10
    ROW_LEN_TH = 13
    ROW_CHOICE1 = 9
    ROW_CHOICE2 = 2
    ITEM_CHOICE1 = 0.4
    ITEM_CHOICE2 = 0.6
    ITEM_CHOICE3 = 0.4
    ITEM_CHOICE4 = 0.9

And it achieved a **100%** win rate against both the pure random agent and the previous best solution, but a **0%** win rate agains the optimal strategy.

## Yanking

Some of the functions and data structures used are the some as those presented by **Prof. Squillero**, albeit some minor modification. Some examples are:<br>
the **Nim** class and the **Nimply** data structure, the functions **evaluate**,**make_strategy**,**pure_random**,**cook_status**,**nim_sum**,**optimal_strategy**