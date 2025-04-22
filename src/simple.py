from collections import deque
from pool import Cycle

def find_simple_cycles(donor_patient_nodes, max_cycle_length):
    ignore = set()
    cycles = []
    donor_patient_nodes.sort(key=lambda n: n.index)
    for start_node in donor_patient_nodes:
        subgraph = create_subgraph(start_node, max_cycle_length, ignore)
        subgraph.sort(key=lambda n: n.index)
        ignore.add(start_node)
        lock = {}
        blist = {}
        stack = deque()

        for inner_node in subgraph:
            lock[inner_node] = float('inf')
            blist[inner_node] = set()

        back_length = cycle_search(subgraph, start_node, start_node, max_cycle_length, 0, lock, blist, stack, cycles)

    return cycles

def cycle_search(subgraph, start_node, node, max_cycle_length, forward_length, lock, blist, stack, cycles):
    back_length = float('inf')
    lock[node] = forward_length
    stack.append(node)
    for e in node.out_edges:
        target_node = e.donor_recipient_node
        if target_node not in subgraph or target_node.index < start_node.index:
            continue
        if target_node == start_node:
            has_altruist = any(n.is_altruist for n in stack)
            cycles.append(Cycle(list(stack), len(stack), len(cycles), has_altruist))
            back_length = 1
        elif (forward_length + 1 < lock[target_node] and forward_length + 1 < max_cycle_length):
            back_length = min(back_length, 1 + cycle_search(subgraph, start_node, target_node, max_cycle_length, forward_length + 1, lock, blist, stack, cycles))
    if back_length < float('inf'):
        relax_locks(node, max_cycle_length, back_length, lock, blist, stack)
    else:
        for e in node.out_edges:
            target_node = e.donor_recipient_node
            if target_node not in subgraph:
                continue
            if node not in blist[target_node]:
                blist[target_node].add(node)
    stack.pop()
    return back_length
    
def relax_locks(node, max_cycle_length, back_length, lock, blist, stack):
    if (lock[node] < max_cycle_length  - back_length + 1):
        lock[node] = max_cycle_length - back_length + 1
        for b_node in blist[node]:
            if b_node not in stack:
                relax_locks(b_node, max_cycle_length, back_length + 1, lock, blist, stack)
        

def create_subgraph(node, max_cycle_length, ignore):
    subgraph = []

    visited = set()
    queue = deque()

    visited.add(node)
    queue.append((node, 0))

    while queue:
        curr_node, curr_level = queue.popleft()
        if curr_level >= max_cycle_length:
            continue 
        subgraph.append(curr_node)
        for e in curr_node.out_edges:
            target_node = e.donor_recipient_node
            if target_node not in visited and target_node not in ignore:
                visited.add(target_node)
                queue.append((target_node, curr_level + 1))
    return subgraph
    

