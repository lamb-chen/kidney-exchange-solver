
from collections import deque, defaultdict
import pool

# used in_seen instead of just checking if node in seen to avoid O(n) lookup time
def tarjans_algorithm(donor_patient_nodes):
    sccs = []
    dfs_index = 0
    stack = deque()
    in_seen = [False] * len(donor_patient_nodes)

    def strong_connect(node):
        nonlocal dfs_index
        node.set_index(dfs_index)
        node.low_link_value = node.index
        stack.append(node)
        in_seen[node.index] = True
        dfs_index += 1

        for edge in node.out_edges:
            target_node = edge.donor_recipient_node
            if target_node.index is None:
                strong_connect(target_node)
                node.set_low_link_value(min(node.low_link_value, target_node.low_link_value))
            
            elif in_seen[target_node.index]:
                node.set_low_link_value(min(node.low_link_value, target_node.low_link_value))

        if node.low_link_value == node.index:
            component = []
            while True:
                stack_node = stack.pop()
                in_seen[stack_node.index] = False
                component.append(stack_node)
                if stack_node.index == node.index:
                    break
            sccs.append(component)

    for node in donor_patient_nodes:
        node.set_index(None)

    for node in donor_patient_nodes:
        if node.index is None:
            strong_connect(node)

    scc_printable_list = []
    for scc in sccs:
        curr_scc = []
        for node in scc:
            curr_scc.append((node.donor.id, node.patient.id))
        scc_printable_list.append(curr_scc)

    return sccs, scc_printable_list


def og_johnsons(scc, max_cycle_length):
    # removed is used to track what node has been "removed" from each 
    # iteration of johnsons for each SCC
    # this is instead of creating a new graph without the node "s" (referring to his paper)
    # use tarjans algorithm to find strongly connected components
    # and then find cycles within each component
    def unblock(node):
        blocked_set.remove(node)
        for blocking_node in blocked_map[node].copy():
            blocked_map[node].remove(blocking_node)
            if blocking_node in blocked_set:
                unblock(blocking_node)

    def circuit(node, max_cycle_length, start_node_idx):
        f = False
        stack.append(node)
        blocked_set.add(node)

        for edge in node.out_edges:
            target_node = edge.donor_recipient_node
            if target_node in removed:
                continue
            if target_node.index == start_node_idx:
                if len(stack) > 1 and len(stack) <= max_cycle_length:
                    has_altruist = any(node.is_altruist for node in stack)
                    cycle_obj = pool.Cycle(list(stack), len(stack), len(found_cycles), has_altruist)
                    found_cycles.append(cycle_obj)
                    f = True
            elif not blocked_set.add(target_node.index) and len(stack) < max_cycle_length:
                    if circuit(target_node, max_cycle_length, start_node_idx):
                        f = True
        if f:
            unblock(node)
        else:
            for edge in node.out_edges:
                target_node = edge.donor_recipient_node
                if not removed[target_node] and node not in blocked_map[target_node]:
                    blocked_map[target_node].add(node)
        stack.pop()
        return f
    found_cycles = []
    removed = set()
    blocked_set = set()
    blocked_map = defaultdict(set)
    stack = deque()
    id_to_node = {}

    scc.sort(key=lambda node: node.index)

    for node in scc:
        id_to_node[node.index] = node

    for node in scc:
        # johnsons treats the graph as if the previous nodes that have already
        # been visited in the scc as if they dont exist
        for edge in node.out_edges:
            target_node = edge.donor_recipient_node 
            if target_node in scc:
                blocked_set.add(target_node.index)
                unblock(target_node)
        circuit(node, max_cycle_length, node.index)
        removed.add(node)

        # new graph
        new_nodes = [n for n in scc if removed[n.index] == False]
        def remover(u_node):
            u_node.out_edges = [e for e in u_node.out_edges if e.donor_recipient_node not in removed]
            return u_node
        cleaned_nodes = list(map(remover, new_nodes))
        return found_cycles + og_johnsons(cleaned_nodes, max_cycle_length)
    return found_cycles
    
def johnsons(donor_patient_nodes, max_cycle_length):
    sccs, scc_printable = tarjans_algorithm(donor_patient_nodes)
    found_cycles = []
    for scc in sccs:
        found_cycles = found_cycles + og_johnsons(sccs, max_cycle_length)
    found_cycles_printable = []
    for cycle in found_cycles:
        cycle_printable = []
        for node in cycle.donor_patient_nodes:
            cycle_printable.append((node.donor.id, node.patient.id))
        found_cycles_printable.append(cycle_printable)
    print(found_cycles_printable)
    print(len(found_cycles_printable))
    
    return found_cycles, found_cycles_printable


