import reader as r
import hierarchical 
import printing
import sys
import weightedsum
import plotting
import johnsons

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename>")
        sys.exit(1)

    print("Reading input file...\n")
    filename = sys.argv[1]
    reader = r.JSONReader()
    pool = reader.read_json(filename)
    print("Finished reading input file.\n")

    print("Finding cycles..\n")
    cycles, found_cycles_printable = johnsons.johnsons(pool.donor_patient_nodes, 3)
    print("Cycle objects created.\n")


    # print("Finding cycles..\n")
    # cycles = pool.create_cycles_objects(3)
    # print("Cycle objects created.\n")

    print("Running Hierarchical solver...\n")
    g_solver = hierarchical.HierarchicalOptimiser(pool, cycles)
    constraint_list = ["MAX_WEIGHT", "MIN_THREE_CYCLES", "MAX_BACKARCS", "MAX_SIZE", "MAX_TWO_CYCLES"]
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




    # print("Running Weighted Sum solver...\n")
    # g_solver = weightedsum.WeightedSumOptimiser(pool, cycles)
    # constraint_list = ["MAX_WEIGHT", "MIN_THREE_CYCLES", "MAX_BACKARCS", "MAX_SIZE", "MAX_TWO_CYCLES"]
    # optimal_cycles, all_selected_cycles = g_solver.optimise(pool, constraint_list)
    # print("\n\nWeighted Sum solver successfully ran.\n")

    # print("Writing to output files...\n")
    # printing.write_all_solutions_to_file(optimal_cycles, all_selected_cycles, "./output/weighted_sum_all_solutions.txt")
    # printing.write_optimal_solution_results(optimal_cycles, pool, "./output/weighted_sum_optimal_solution_results.txt")
    # print("Finished writing to output files.\n")

    # print("Plotting graphs...\n")
    # solver_type = "weighted_sum"
    # plotter = plotting.Plot(optimal_cycles, pool.donor_patient_nodes, solver_type)
    # plotter.plot_graph()
    # print("Finished plotting graphs.\n")

    print("Program successfully completed.\n")
