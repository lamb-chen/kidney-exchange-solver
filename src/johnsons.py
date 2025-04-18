
from collections import deque, defaultdict
import pool

# used in_seen instead of just checking if node in seen to avoid O(n) lookup time
def tarjans_algorithm(donor_patient_nodes):
    sccs = []
    dfs_index = [0]
    seen = deque()
    in_seen = [False] * len(donor_patient_nodes)

    def strong_connect(node, dfs_index):
        node.set_index(dfs_index[0])
        node.low_link_value = dfs_index[0]
        seen.append(node)
        in_seen[dfs_index[0]] = True
        dfs_index[0] += 1

        for edge in node.out_edges:
            target_node = edge.donor_recipient_node
            if target_node.index is None:
                strong_connect(target_node, dfs_index)
                if in_seen[target_node.index]:
                    node.set_low_link_value(min(node.low_link_value, target_node.low_link_value))
            
            elif in_seen[target_node.index]:
                node.set_low_link_value(min(node.low_link_value, target_node.low_link_value))

        if node.low_link_value == node.index:
            component = []
            while True:
                stack_node = seen.pop()
                in_seen[stack_node.index] = False
                component.append(stack_node)
                if stack_node.index <= node.index:
                    break
            component.sort(key=lambda node: node.index)
            sccs.append(component)


    for node in donor_patient_nodes:
        if node.index is None:
            strong_connect(node, dfs_index)
    sccs.sort(key=lambda component: component[0].index)

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
    removed = [False] * len(donor_patient_nodes)
    # use tarjans algorithm to find strongly connected components
    # and then find cycles within each component
    def circuit(node, max_cycle_length, start_node_idx):
        def unblock(node):
            is_blocked[node.index] = False
            for blocking_node in blocked_map[node.index]:
                blocked_map[node.index].remove(blocking_node)
                if is_blocked[node.index]:
                    unblock(node)

        f = False
        stack.append(node)
        is_blocked[node.index] = True

        for edge in node.out_edges:
            target_node = edge.donor_recipient_node
            if removed[target_node.index]:
                continue
            if target_node.index == start_node_idx:
                if len(stack) > 1 and len(stack) <= max_cycle_length:
                    has_altruist = False
                    for node in stack:
                        if node.is_altruist:
                            has_altruist = True
                    cycle_obj = pool.Cycle(list(stack), len(stack), len(found_cycles), has_altruist)
                    found_cycles.append(cycle_obj)
                    f = True
            elif not is_blocked[target_node.index] and len(stack) < max_cycle_length:
                    if circuit(target_node, max_cycle_length, start_node_idx):
                        f = True
        if f:
            unblock(node)
        else:
            for edge in node.out_edges:
                target_node = edge.donor_recipient_node
                if node.index not in blocked_map[target_node.index]:
                    blocked_map[target_node.index].append(node.index)
        stack.pop()
        return f

    sccs, scc_printable = tarjans_algorithm(donor_patient_nodes)

    for scc in sccs:
        is_blocked = [False] * len(donor_patient_nodes)
        blocked_map = defaultdict(list)
        stack = deque()
        for node in scc:
            # johnsons treats the graph as if the previous nodes that have already
            # been visited in the scc as if they dont exist
            if removed[node.index]:
                continue
            for edge in node.out_edges:
                target_node = edge.donor_recipient_node 
                is_blocked[target_node.index] = False
                blocked_map[target_node.index].clear()
            circuit(node, max_cycle_length, node.index)
            removed[node.index] = True

    found_cycles_printable = []
    for cycle in found_cycles:
        cycle_printable = []
        for node in cycle.donor_patient_nodes:
            cycle_printable.append((node.donor.id, node.patient.id))
        found_cycles_printable.append(cycle_printable)

    return found_cycles, found_cycles_printable