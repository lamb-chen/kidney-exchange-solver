def print_pool_donor_nodes(pool):
    for donor_patient_node in pool.donor_patient_nodes:
        donor_id = donor_patient_node.donor
        print(f"Donor ID: {donor_id}")
        for recipient_with_score in donor_patient_node.recipient_patients:
            print(f"  Recipient Patient ID: {recipient_with_score.recipient_patient}")

def print_graph(pool):
        print("Altruists:")
        for altruist in pool.altruists:
            print(f"Altruist ID: {altruist.id}, Age: {altruist.dage}")
            for edge in altruist.out_edges:
                print(f">> Recipient Patient ID: {edge.target_donor_patient_node.patient.id}, Score: {edge.score}")

        print("\nDonor-Patient Nodes:")
        for donor_patient_node in pool.donor_patient_nodes:
            print(f"Donor ID: {donor_patient_node.donor.id}, Age: {donor_patient_node.donor.dage}, Patient ID: {donor_patient_node.patient.id}")
            for edge in donor_patient_node.out_edges:
                print(f">> Donor Recipient Node: Donor ID: {edge.donor_recipient_node.donor.id}, Patient ID: {edge.donor_recipient_node.patient.id}, Score: {edge.score}")
            for recipient_with_score in donor_patient_node.recipient_patients:
                print(f">> Recipient Patient ID: {recipient_with_score.recipient_patient}, Score: {recipient_with_score.score}")

def print_cycles(cycles):
    print("\nChecking cycles:")
    count = 0
    for cycle in cycles:  
        count += 1
        print("\nCycle:", count)
        for node in cycle.donor_patient_nodes:  
            print("Donor:", node.donor.id, "Patient:", node.patient.id)
        print("cycle: ", cycle.index, "weight: ", cycle.get_cycle_weight())
        print("Num of backarcs: ", cycle.find_num_of_backarcs())
        print("\n")

def print_graph_connectivity(pool):
    print("\nChecking graph connectivity:")
    for node in pool.donor_patient_nodes:
        print(f"\nNode: Donor {node.donor.id}, Patient {node.patient.id}")
        print(f"Number of outgoing edges: {len(node.out_edges)}")
        for edge in node.out_edges:
            print(f"Edge to: Donor {edge.donor_recipient_node.donor.id}, Patient {edge.donor_recipient_node.patient}")

def print_optimal_cycles(optimal_cycles):
    for cycle in optimal_cycles:
        print("\nChosen cycle: ", cycle.index)
        for node in cycle.donor_patient_nodes:
            print("Donor: ", node.donor.id, "Patient: ", node.patient.id)


def print_all_selected_cycles(all_selected_cycles):
    if all_selected_cycles:
        print("\n  Selected Cycles:")
        for cycle in all_selected_cycles:
            donors = [node.donor.id for node in cycle.donor_patient_nodes]
            recipients = [node.patient.id for node in cycle.donor_patient_nodes]
            print(f"    Cycle {cycle.index}: Donors {donors}, Recipients {recipients}")
    else:
        print("No cycles selected in this solution.")


def write_all_solutions_to_file(optimal_cycles, all_selected_cycles, filename):
    with open(filename, 'w') as file:
        file.write("Final Chosen Optimal Exchanges\n\n")
        for cycle in optimal_cycles:
            file.write(f"   Cycle {cycle.index}:\n")
            for node in cycle.donor_patient_nodes:
                file.write(f"      Donor: {node.donor.id}, Patient: {node.patient.id}\n")
        file.write("\n###################################################################################\n")
        
        file.write("\nAll Selected Cycles\n")
        if all_selected_cycles:
            for i, selected_cycles in enumerate(all_selected_cycles):
                if selected_cycles:
                    file.write(f"\nSolution {i} Cycles: \n")
                    for cycle in selected_cycles:
                        nodes = [(node.donor.id, node.patient.id) for node in cycle.donor_patient_nodes]
                        file.write(f"   Cycle {cycle.index}: Nodes: {nodes}\n")
        else:
            file.write("No cycles selected in this solution.\n")

def write_optimal_solution_results(optimal_cycles, pool, filename):
    # donors here refers to non-altruistic donors
    total_nodes = len(pool.donor_patient_nodes)
    
    total_num_of_patients = len(pool.patients)
    selected_patient_count = sum(1 for cycle in optimal_cycles for node in cycle.donor_patient_nodes if not node.is_altruist)
    
    total_num_of_donors = len(pool.patients)
    selected_donor_count = selected_patient_count

    total_num_of_altruists = len(pool.altruists)
    selected_altruist_count = sum(1 for cycle in optimal_cycles for node in cycle.donor_patient_nodes if node.is_altruist)

    total_cycles = sum(1 for cycle in pool.all_cycles if not cycle.is_chain)
    selected_cycle_count = sum(1 for cycle in optimal_cycles if not cycle.is_chain)

    total_three_cycles = sum(1 for cycle in pool.all_cycles if cycle.length == 3 and not cycle.is_chain)
    selected_three_cycles = sum(1 for cycle in optimal_cycles if cycle.length == 3 and not cycle.is_chain)

    total_two_cycles = sum(1 for cycle in pool.all_cycles if cycle.length == 2 and not cycle.is_chain)
    selected_two_cycles = sum(1 for cycle in optimal_cycles if cycle.length == 2 and not cycle.is_chain)

    total_chains = sum(1 for cycle in pool.all_cycles if cycle.is_chain)
    selected_chains = sum(1 for cycle in optimal_cycles if cycle.is_chain)

    # total_weight = sum(cycle.get_cycle_weight() for cycle in pool.cycles)
    selected_exchanges_weight = sum(cycle.get_cycle_weight() for cycle in optimal_cycles)

    selected_num_of_backarcs = sum(cycle.find_num_of_backarcs() for cycle in optimal_cycles)

    total_highly_sensitised_count = sum(
        1 for patient in pool.patients.values()
        if patient.cpra is not None
        if patient.cpra > 0.85
    )

    selected_highly_sensitised_count = sum(
        1 for cycle in optimal_cycles for node in cycle.donor_patient_nodes 
        if node.patient.cpra is not None
        if node.patient.cpra > 0.85
    )       
    with open(filename, 'w') as file:
        file.write("Final Chosen Optimal Exchanges\n")

        file.write(f"\nTotal potential nodes: {total_nodes}")
        file.write(f"\nTotal number of patients: {total_num_of_patients}")
        file.write(f"\nNumber of selected patients: {selected_patient_count}")
        file.write(f"\nTotal number of donors: {total_num_of_donors}")
        file.write(f"\nNumber of selected donors: {selected_donor_count}")
        file.write(f"\nTotal number of altruists: {total_num_of_altruists}")
        file.write(f"\nNumber of selected altruists: {selected_altruist_count}") 
        file.write(f"\nTotal number of highly sensitised patients: {total_highly_sensitised_count}")
        file.write(f"\nNumber of selected highly sensitised patients: {selected_highly_sensitised_count}")   

        file.write(f"\n\nTotal potential cycles: {total_cycles}")
        file.write(f"\nNumber of selected cycles: {selected_cycle_count}")        
        file.write(f"\nTotal potential three-cycles: {total_three_cycles}")
        file.write(f"\nNumber of selected three-cycles: {selected_three_cycles}")        
        file.write(f"\nTotal potential two-cycles: {total_two_cycles}")
        file.write(f"\nNumber of selected two-cycles: {selected_two_cycles}")        
        file.write(f"\nTotal potential chains: {total_chains}")
        file.write(f"\nNumber of selected chains: {selected_chains}")   
        file.write(f"\nNOTE: Cycles and chains here are differentiated once again.\nCycles does not include pseudo-cycles.")

        file.write(f"\n\nNumber of backarcs in final exchange set: {selected_num_of_backarcs}")        


        file.write(f"\n\nFinal optimal exchange set weight: {selected_exchanges_weight}")    

        file.write(f"\nSelected Cycles: \n")
        for cycle in optimal_cycles:
            file.write(f"   Cycle {cycle.index}:\n")
            for node in cycle.donor_patient_nodes:
                file.write(f"      Donor: {node.donor.id}, Patient: {node.patient.id}\n")
        file.write("\n###################################################################################\n")

