# Kidney Exchange Solver
This kidney exchange program solver includes:
1) implementation of the hierarchical model from the *Paired and Altruistic Kidney Donation in the UK: Algorithms and Experimentation* 2015 paper. [For reference, the paper can be found here](https://dl.acm.org/doi/10.1145/2670129)
2) implementation of a weighted sum version, using the same criteria determined by NHSBT mentioned in the paper
3) graphical visualisation of the final optimal exchanges chosen amongst the original graph

The project was created as part of my final year dissertation for my undergraduate Computer Science degree.

## Dependencies
Require pre-installation of Gurobi. [Instructions for installation can be found here.](https://support.gurobi.com/hc/en-us/articles/14799677517585-Getting-Started-with-Gurobi-Optimizer)
Note: a license must be accquired. This project was created with the free academic license.

## How to run
Command:
```
python main.py -f="filename" -w="y" -c=3
```
The above command runs the weighted_sum version of the solver on the dataset specified by the filename (must be JSON), and has a maximum cycle length of 3.   
To run the hierarchical version, use `-w="n"` instead.   

```
All Flag Options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Input file name
  -w WEIGHTED_SUM, --weighted_sum WEIGHTED_SUM
                        y/n, no means solver will run hierarchical optimisation
  -c CYCLE, --cycle CYCLE
                        Maximum cycle length
```

## Understanding the output
The program has 3 types of output:
1) Printed output in the terminal
2) A .txt file containing the selected optimal exchanges. In addition this includes other solutions that were not chosen.
3) HTML file containing a graphical visualisation of the original graph and with the chosen optimal exchanges highlighted. Example graph:
