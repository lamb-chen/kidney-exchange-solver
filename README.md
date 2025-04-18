# Kidney Exchange Solver
This kidney exchange program solver includes:
1) implementation of the hierarchical model from the *Paired and Altruistic Kidney Donation in the UK: Algorithms and Experimentation* 2015 paper. [For reference, the paper can be found here](https://dl.acm.org/doi/10.1145/2670129)
2) implementation of a new weighted sum version, using the same criteria determined by NHSBT mentioned in the paper
3) graphical visualisation of the final optimal exchanges chosen amongst the original graph

The project was created as part of my final year dissertation for my undergraduate Computer Science degree.

## Dependencies
Require pre-installation of Gurobi. [Instructions for installation can be found here.](https://support.gurobi.com/hc/en-us/articles/14799677517585-Getting-Started-with-Gurobi-Optimizer)
Note: a license must be accquired. This project was created with the free academic license.

## How to run
Command:
```
python main.py -f="filename" -l="y" -c=3
```
The above command runs the lexcographical/hierarchical version of the solver on the dataset specified by the filename (must be JSON), and has a maximum cycle length of 3.   
To run the weighted sum version, use `-l="n"` instead.   

```
All Flag Options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Input file name
  -l LEX, --lex LEX     y/n, yes will run lexcographic/hierarchical optimisation, no means solver will run weighted sum optimisation
  -w WEIGHTS, --weights WEIGHTS
                        List of 5 weights for each criteria e.g., '--weights 0.1 0.2 0.7' or '--weights 0.1,0.2,0.7' The order corresponds to the order of the criteria: MAX_WEIGHT, MIN_THREE_CYCLES, MAX_BACKARCS, MAX_SIZE,
                        MAX_TWO_CYCLES
  -c CYCLE, --cycle CYCLE
                        Maximum cycle length
```

## Understanding the output
The program has 3 types of output:
1) Printed output in the terminal
2) A .txt file containing the selected optimal exchanges. In addition this includes other solutions that were not chosen.
3) A .txt file containing the final objective function values for each objective in each solution (including the ones that were not chosen).
4) HTML file containing a graphical visualisation of the original graph and with the chosen optimal exchanges highlighted.

Example small instance graph:    
<img src="https://github.com/lamb-chen/kidney-exchange-solver/blob/main/resources/small_instance_2.png" width="300">  

Example large instance graph:   
<img src="https://github.com/lamb-chen/kidney-exchange-solver/blob/main/resources/large_instance.png" width="300"> 
