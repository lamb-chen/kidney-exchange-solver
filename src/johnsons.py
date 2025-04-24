
from collections import deque, defaultdict
from copy import copy, deepcopy
import pool

# used in_seen instead of just checking if node in seen to avoid O(n) lookup time
def tarjans_algorithm(donor_patient_nodes):
    sccs = []
    dfs_index = 0
    seen = deque()
    in_seen = [False] * len(donor_patient_nodes)

    def strong_connect(node):
        nonlocal dfs_index
        node.set_dfs_index(dfs_index)
        node.low_link_value = dfs_index
        seen.append(node)
        in_seen[dfs_index] = True
        dfs_index += 1

        for edge in node.out_edges:
            target_node = edge.donor_recipient_node
            if target_node.dfs_index is None:
                strong_connect(target_node)
                node.set_low_link_value(min(node.low_link_value, target_node.low_link_value))
            
            elif in_seen[target_node.dfs_index]:
                node.set_low_link_value(min(node.low_link_value, target_node.low_link_value))

        if node.low_link_value == node.dfs_index:
            component = []
            while True:
                stack_node = seen.pop()
                in_seen[stack_node.dfs_index] = False
                component.append(stack_node)
                if stack_node.dfs_index <= node.dfs_index:
                    break
            sccs.append(component)


    for node in donor_patient_nodes:
        if node.dfs_index is None:
            strong_connect(node)

    scc_printable_list = []
    for scc in sccs:
        curr_scc = []
        for node in scc:
            curr_scc.append((node.donor.id, node.patient.id))
        scc_printable_list.append(curr_scc)

    return sccs, scc_printable_list


def johnsons(donor_patient_nodes, max_cycle_length):
    found_cycles = []
    # removed is used to track what node has been "removed" from each 
    # iteration of johnsons for each SCC
    # this is instead of creating a new graph without the node "s" (referring to his paper)
    # use tarjans algorithm to find strongly connected components
    # and then find cycles within each component
    def unblock(node, is_blocked, blocked_map, id_to_node):
        is_blocked[node.dfs_index] = False
        for blocking_node_index in blocked_map[node.dfs_index].copy():
            blocked_map[node.dfs_index].remove(blocking_node_index)
            if is_blocked[blocking_node_index]:
                unblock(id_to_node[blocking_node_index], is_blocked, blocked_map, id_to_node)

    def circuit(node, max_cycle_length, start_node_idx, removed, is_blocked, blocked_map, stack, id_to_node):
        f = False
        stack.append(node)
        is_blocked[node.dfs_index] = True

        all_removed = []
        for edge in node.out_edges:
            target_node = edge.donor_recipient_node
            all_removed.append(removed[target_node.dfs_index])
        
        if False not in all_removed: return True

        for edge in node.out_edges:
            target_node = edge.donor_recipient_node
            if removed[target_node.dfs_index]: continue
            elif target_node not in scc or target_node.dfs_index < start_node_idx: continue
            if target_node.dfs_index == start_node_idx:
                if len(stack) > 1 and len(stack) <= max_cycle_length:
                    has_altruist = False
                    for node in stack:
                        if node.is_altruist:
                            has_altruist = True
                    cycle_obj = pool.Cycle(list(stack), len(stack), len(found_cycles), has_altruist)
                    found_cycles.append(cycle_obj)
                    f = True
            elif not is_blocked[target_node.dfs_index] and len(stack) < max_cycle_length:
                    if circuit(target_node, max_cycle_length, start_node_idx, removed, is_blocked, blocked_map, stack, id_to_node):
                        f = True
        if f:
            unblock(node, is_blocked, blocked_map, id_to_node)
        else:
            for edge in node.out_edges:
                
                target_node = edge.donor_recipient_node
                # if removed[target_node.dfs_index]: continue
                if node.dfs_index not in blocked_map[target_node.dfs_index]:
                    blocked_map[target_node.dfs_index].add(node.dfs_index)
        stack.pop()
        # is_blocked[node.dfs_index] = False
        return f

    sccs, scc_printable = tarjans_algorithm(donor_patient_nodes)

    for scc in sccs:
        removed = [False] * len(donor_patient_nodes)
        is_blocked = [False] * len(donor_patient_nodes)
        blocked_map = defaultdict(set)
        id_to_node = {}

        scc.sort(key=lambda node: node.dfs_index)

        for node in scc:
            id_to_node[node.dfs_index] = node

        for node in scc:
            stack = deque()
            # for n in scc: unblock(n, is_blocked, blocked_map, id_to_node)
            is_blocked = [False] * len(donor_patient_nodes)
            blocked_map = defaultdict(set)
            circuit(node, max_cycle_length, node.dfs_index, removed, is_blocked, blocked_map, stack, id_to_node)
            removed[node.dfs_index] = True

    found_cycles_printable = []
    for cycle in found_cycles:
        cycle_printable = []
        for node in cycle.donor_patient_nodes:
            cycle_printable.append((node.donor.id, node.patient.id))
        found_cycles_printable.append(cycle_printable)
    print(found_cycles_printable)
    print(len(found_cycles_printable))
    
    return found_cycles, found_cycles_printable