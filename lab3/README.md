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


## Strategy 3: MinMax

The third strategy is based on deriving an agent using MinMax techniques.

### State evaluation

The states, represented by the **current board** can be evaluated as **0, 1** or **-1**.<br>
A state is evaluated as **-1** when the agent has **already lost** (the board is empty) or (since optimal play from the opponent is assumed) if the current state has **nim sum equal to 0**.<br>
A state is evaluated as **1** when **victory is guaranteed** (only one non-empty row left on the board)<br>
All other states are evaluated as **0**

### Memoization

The state tree is generated with **no depth bounds**, some keeping track of previously considered states is essential.<br>
To do this, **tuples** representing states are used to access 2 dictionaries: **knownStates** and **actions**.<br>
The former stores, for each state, its evaluation, while the latter stores the ply that is been previously decided to make in that state.

### Algorithm

Whenever **minMax** is called on a given state, it is checked whether it was previously encountered. If so, the corresponding action is **immediately** returned.<br>
Otherwise, the state is evaluated: if the result is **1**, the winning action is taken immediately; if the result is **-1** an item is removed from the first active row (if it exists) since against an optimal strategy every move would have the same losing outcome.

If the state is **neutral**, then all the possible moves starting from that state are considered and the hypotetical **following state** is visited recursively.<br>
In order to prune useless branches, a bound is initialized before iterating on the possible moves and branches that are sure not to be chosen by agent are discarded.<br>
Following the MinMax strategy, each height level in the state tree is alternated between **minimization** and **maximization**.

## Results

Playing **100** games (**50** as player 1 and **50** as player 2) on a board with **6** rows, the MinMax agent is able to achieve a **100%** winrate against the random strategy and a **50%** winrate against the optimal strategy


## Strategy 4: Reinforcement learning

The approached followed is similar to the one presented for the **maze** during lectures. The trainee agent, at each move, randomly chooses to perform a **random move** or a **policy driven** move

### State initialization

In order to avoid initializing a reward for every single possible state at once, rewards for each state are inizialized every time the agent discovers a new state. The initial value is set to **-0.5**, which means that the agent is doubtful of states that have never been seen before.

### Rewards

The reward for a state is calculated at the end of each move (**both** the trainee and the training opponent), **clear** winning and losing states are valued as **+/- 5** while states with **only one row left** are valued as **+/- 3** because they can potentially take to the end of the game; **neutral** states have a reward of **0**.

### Learning

At the end of each game, the **state history** is scanned and rewards are adjusted based on the result of the game. Also, the **random factor** is changed according to the reward accumulated during the course of the game: if the result is a loss, the random factor is slightly **increased**, while it's **decreased** if the result was a win.

### Results

After **2000** games of training (**1000** against **pure random** and then **1000** against the **optimal strategy**), the end result is around a **40%** win rate against the **pure random** (not very promising) and around **20%** win rate against the **optimal strategy**. This is rather surprising, it seems that the agent is capable of playing optimally but that doesn't seem to be very effective against all other kinds of agents.



## Yanking

Some of the functions and data structures used are the some as those presented by **Prof. Squillero**, albeit some minor modification. Some examples are:<br>
the **Nim** class and the **Nimply** data structure, the functions **evaluate**,**make_strategy**,**pure_random**,**cook_status**,**nim_sum**,**optimal_strategy** and the overall structure of the **MinMax approach for tic-tac-toe** shown during the lectures