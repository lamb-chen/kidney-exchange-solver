from collections import namedtuple, defaultdict

class Altruist(object):
    def __init__(self, id, dage):
        self.id = id
        self.dage = dage
        self.recipient_patients = []
        self.out_edges = []
        self.mip_vars = []
        self.mip_unmatched = None
    
    def add_recipient(self, recipient_patient, score):
        self.recipient_patients.append(RecipientWithScore(recipient_patient, score))

    def add_edge(self, target_donor_patient_node, score):
        self.out_edges.append(AltruistEdge(self, target_donor_patient_node, score=score))

class AltruistEdge(object):
    def __init__(self, altruist, target_donor_patient_node, score):
        self.altruist = altruist
        self.target_donor_patient_node = target_donor_patient_node
        self.score = score

class Patient(object):
    def __init__(self, id):
        self.id = id
        self.mip_vars = []

class Donor(object):
    def __init__(self, id, dage):
        self.id = id
        self.dage = dage
        self.mip_vars = []
    
class DonorPatientNode(object):
    def __init__(self, donor, patient, is_altruist=False):
        self.donor = donor
        self.patient = patient
        self.recipient_patients = []
        self.out_edges = []
        self.is_altruist = is_altruist
        self.low_link_value = None
        self.index = None
    
    def set_index(self, index):
        self.index = index
    
    def set_low_link_value(self, low_link_value):
        self.low_link_value = low_link_value

    def add_edge(self, target_donor_patient_node, score):
        self.out_edges.append(DonorPatientEdge(target_donor_patient_node, score=score))

    def add_recipient(self, recipient_patient, score):
        self.recipient_patients.append(RecipientWithScore(recipient_patient, score))

    def add_recipients(self, recipient_patient_list):
        self.recipient_patients.extend(recipient_patient_list)

class DonorPatientEdge(object):
    def __init__(self, donor_recipient_node, score):
        self.donor_recipient_node = donor_recipient_node
        self.score = score

class Cycle(object):
    def __init__(self, donor_patient_nodes, length, index, is_chain=False):
        self.donor_patient_nodes = donor_patient_nodes
        self.mip_var = None
        self.length = length
        self.index = index
        self.is_chain = is_chain
    
    def find_num_of_backarcs(self):
        backarcs = 0
        for i in range(len(self.donor_patient_nodes)):
            curr_node = self.donor_patient_nodes[i]
            prev_node = self.donor_patient_nodes[i-1]
            for edge in curr_node.out_edges:
                if edge.donor_recipient_node == prev_node: 
                    backarcs += 1
        return backarcs

    def get_cycle_weight(self):
        total_score = 0
        for i in range(len(self.donor_patient_nodes)):
            current_node = self.donor_patient_nodes[i]
            next_node = self.donor_patient_nodes[(i + 1) % len(self.donor_patient_nodes)]
    
            for edge in current_node.out_edges:
                if edge.donor_recipient_node == next_node:
                    total_score += edge.score
                    break
        return total_score

class Pool():
    def __init__(self):
        self.patients = {}
        self.donor_patient_nodes = []
        self.altruists = []

    # def add_patient(self, patient):
    #     self.patients.append(patient)
    
    def add_donor_patient_node(self, donor_patient_node):
        self.donor_patient_nodes.append(donor_patient_node)

    def add_edges_to_nodes(self):
        # id_to_nodes is a dict that stores the patient ids as the key
        # and the corresponding donor_patient_nodes that the patient is
        # related to
        patient_id_to_nodes = defaultdict(list)
        for node in self.donor_patient_nodes:
            patient_id_to_nodes[node.patient.id].append(node)

        idx = 0
        altruist_dp_nodes = []
        # associate each altruist with a dummy recipient to create a dummy
        # donor patient node
        for altruist in self.altruists:
            dummy_recipient_id = f"dummy_{idx}" 
            dummy_node = Patient(dummy_recipient_id)
            dummy_dp = DonorPatientNode(altruist, dummy_node, is_altruist=True)
            dummy_dp.add_recipients(altruist.recipient_patients)
            altruist_dp_nodes.append(dummy_dp)
            idx += 1

        # then need to append the altruist matches i.e. out going edge from the altruist node
        # this is not the actual edge as only know the recipient
        # actually i think this is covered by the for loops below?
        self.donor_patient_nodes.extend(altruist_dp_nodes)

        # for each donor patient node, the corresponding donor
        # to the recipient patient is found through the id_to_nodes list
        for donor_patient_node in self.donor_patient_nodes:
            for recipient_with_score in donor_patient_node.recipient_patients:
                recipient_patient_id = recipient_with_score.recipient_patient
                score = recipient_with_score.score
                if recipient_patient_id in patient_id_to_nodes:
                    for recipient_node in patient_id_to_nodes[recipient_patient_id]:
                        donor_patient_node.add_edge(recipient_node, score)
        

        # OKAY NOW NEED TO ADD ALL THE DUMMY EDGES 
        # for each altruist, add the edges of the donors 

        for donor_patient_node in self.donor_patient_nodes:
            if not donor_patient_node.is_altruist:
                for altruist_node in altruist_dp_nodes:
                    # the paper states the weight is set to 0
                    donor_patient_node.add_edge(altruist_node, 0)

    def find_cycles(self, max_length):
        cycles = set()
        added = set()
        for start_node in self.donor_patient_nodes:
            path = []
            visited = set()

            def dfs(current_node):
                if len(path) > max_length:
                    return
                # frozenset used to help remove duplicates in the tuples
                if path and current_node == start_node and len(path) in range(2, max_length + 1):
                    if frozenset(path) not in added:
                        cycles.add(tuple(path))
                        added.add(frozenset(path))
                    return
                    
                if current_node in visited:
                    return
                    
                visited.add(current_node)
                path.append(current_node)
                
                for edge in current_node.out_edges:
                    next_node = edge.donor_recipient_node
                    dfs(next_node)
                
                path.pop()
                visited.remove(current_node)
                return
            
            dfs(start_node)
        return cycles

    def create_cycles_objects(self, max_length):
        idx = 0

        final_cycles = []
        found_cycles = self.find_cycles(max_length)
        is_chain = False
        for cycle in found_cycles:
            for node in cycle:
                if node.is_altruist:
                    is_chain = True
            final_cycles.append(Cycle(list(cycle), len(cycle), idx, is_chain))
            idx += 1

        return final_cycles

RecipientWithScore = namedtuple('RecipientWithScore', ['recipient_patient', 'score'])