import reader as r
import hierarchical 
import printing
import sys
import weightedsum
import plotting
import argparse
import simple
import normalisation

# allow comma-separated or space-separated weights as input
def parse_weights(arg):
    try:
        arg = arg.replace(',', ' ')
        weights = [float(x.strip()) for x in arg.split()]
        if len(weights) != 5:
            raise argparse.ArgumentTypeError("Required exactly 5 weights for --weights")
        return weights
    except ValueError:
        raise argparse.ArgumentTypeError("Weights must be numbers.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kidney exchange optimisation solver")

    parser.add_argument("-f", "--file", help="Input file name", type=str,
                        required=True)
    
    parser.add_argument("-l", "--lex",
                        help="y/n, yes will run lexcographic/hierarchical optimisation,\nno means solver will run normaliser or weighted sum optimisation",
                        choices=["y", "n"],
                        required=True)

    parser.add_argument("-n", "--normalise",
                        help="y/n, yes will run normaliser",
                        choices=["y", "n"],
                        required=True)
    
    parser.add_argument(
        '-w', '--weights',
        type=parse_weights,
        required=False,
        help="Only necessary when running weighted sum model. List of 5 weights for each criteria\ne.g., '--weights 0.1 0.2 0.7' or '--weights 0.1,0.2,0.7'\nThe order corresponds to the order of the criteria: MAX_WEIGHT, MIN_THREE_CYCLES, MAX_BACKARCS, MAX_SIZE, MAX_TWO_CYCLES\n"
    )
        
    parser.add_argument("-c", "--cycle",
                        help="Maximum cycle length",
                        type=int,
                        required=True)
    args = parser.parse_args()

    max_cycle_length = args.cycle

    weights_list = args.weights

    if args.lex == 'n' and args.normalise == 'n' and not args.weights:
        parser.error("--weights is required when --lex is 'n' i.e. when running weighted sum model")

    if args.file.endswith(".json"):
        print("Reading input file...\n")
        filename = sys.argv[1]
        reader = r.JSONReader()
        pool = reader.read_json(args.file)
        print("Finished reading input file.\n")

        print("Finding cycles..\n")
        cycles = simple.find_simple_cycles(pool.donor_patient_nodes, max_cycle_length)
        pool.all_cycles = cycles
        print("Cycle objects created.\n")

        if args.lex == "n":
            if args.normalise == "y":
                print("Running normaliser...\n")
                g_solver = normalisation.Normaliser(pool, cycles)
                constraint_list = ["MAX_WEIGHT", "MAX_BACKARCS", "MIN_THREE_CYCLES", "MAX_SIZE", "MAX_TWO_CYCLES"]
                max_values = g_solver.find_max_values(pool, constraint_list)
                print("\n", max_values)
                print("\n\nNormaliser successfully ran.\n")
                print("Program successfully completed.\n")

            else:
                print("Running Weighted Sum solver...\n")
                g_solver = weightedsum.WeightedSumOptimiser(pool, cycles, weights_list)
                constraint_list = ["MAX_WEIGHT", "MAX_BACKARCS", "MIN_THREE_CYCLES", "MAX_SIZE", "MAX_TWO_CYCLES"]
                optimal_cycles, all_selected_cycles = g_solver.optimise(pool, constraint_list)
                print("\n\nWeighted Sum solver successfully ran.\n")

                print("Writing to output files...\n")
                printing.write_all_solutions_to_file(optimal_cycles, all_selected_cycles, "./output/weighted_sum_all_solutions.txt")
                printing.write_optimal_solution_results(optimal_cycles, pool, "./output/weighted_sum_optimal_solution_results.txt")
                print("Finished writing to output files.\n")

                print("Plotting graphs...\n")
                solver_type = "weighted_sum"
                plotter = plotting.Plot(optimal_cycles, pool.donor_patient_nodes, solver_type)
                plotter.plot_graph()
                print("Finished plotting graphs.\n")
                print("Program successfully completed.\n")

        elif args.lex == "y":
            print("Running Hierarchical solver...\n")
            g_solver = hierarchical.HierarchicalOptimiser(pool, cycles)
            # put in order of least important to most
            constraint_list = ["MAX_WEIGHT", "MAX_BACKARCS", "MIN_THREE_CYCLES", "MAX_SIZE", "MAX_TWO_CYCLES"]
            optimal_cycles, all_selected_cycles = g_solver.optimise(pool, constraint_list)
            print("\n\nHierarchical solver successfully ran.\n")

            print("Writing to output files...\n")
            printing.write_all_solutions_to_file(optimal_cycles, all_selected_cycles, "./output/hierarchical_all_solutions.txt")
            printing.write_optimal_solution_results(optimal_cycles, pool, "./output/hierarchical_optimal_solution_results.txt")
            print("Finished writing to output files.\n")

            print("Plotting graphs...\n")
            solver_type = "hierarchical"
            plotter = plotting.Plot(optimal_cycles, pool.donor_patient_nodes, solver_type)
            plotter.plot_graph()
            print("Finished plotting graphs.\n")
        else:
            print('Must put "y" or "n" for --lex')

    else:
        print("Input file must be in valid JSON format")