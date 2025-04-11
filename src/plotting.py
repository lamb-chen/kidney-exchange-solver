import networkx as nx
from pyvis.network import Network

class Plot():
    def __init__(self, optimal_cycles, donor_patient_nodes, solver_type):
        self.graph = nx.DiGraph()
        self.selected_graph = nx.DiGraph()
        self.donor_patient_nodes = donor_patient_nodes
        self.optimal_cycles = optimal_cycles
        self.added_nodes = set() 
        self.selected_nodes = set()
        self.selected_edges = set()
        self.solver_type = solver_type

    def _plot_selected_cycles(self):
        colour = '#faa7a7'
        for cycle in self.optimal_cycles:
            last_node = None  

            for _, node in enumerate(cycle.donor_patient_nodes):
                if node.is_altruist:
                    node_id = f"{node.donor.id}"
                    if node_id not in self.selected_nodes:
                        self.selected_graph.add_node(node_id, label=node_id, color=colour)
                        self.selected_nodes.add(node_id)

                    # altruist node must not have ingoing edges
                    if last_node is not None:
                        last_node_id = f"{last_node.donor.id}" if last_node.is_altruist else f"{last_node.donor.id}, {last_node.patient.id}"
                        self.selected_graph.add_edge(node_id, last_node_id, color=colour)
                        self.selected_edges.add((node_id, last_node_id))

                    last_node = node 

                else:
                    node_id = f"{node.donor.id}, {node.patient.id}"
                    if node_id not in self.selected_nodes:
                        self.selected_graph.add_node(node_id, label=node_id, color=colour)
                        self.selected_nodes.add(node_id)

                    if last_node is not None:
                        last_node_id = f"{last_node.donor.id}, {last_node.patient.id}"
                        self.selected_graph.add_edge(last_node_id, node_id, color=colour)
                        self.selected_edges.add((last_node_id, node_id))

                    last_node = node  

            # if cycle is meant to be a chain don't add edge from last to first node i.e. complete cycle 
            if not cycle.is_chain:
                first_node = cycle.donor_patient_nodes[0]
                last_node_id = f"{last_node.donor.id}" if last_node.is_altruist else f"{last_node.donor.id}, {last_node.patient.id}"
                first_node_id = f"{first_node.donor.id}" if first_node.is_altruist else f"{first_node.donor.id}, {first_node.patient.id}"
                self.selected_graph.add_edge(last_node_id, first_node_id, color = colour)
                self.selected_edges.add((last_node_id, first_node_id))

        net = Network(notebook=True, filter_menu=True, cdn_resources='remote', directed=True)
        net.from_nx(self.selected_graph)
        net.write_html(f"./output/{self.solver_type}_selected_graph.html")

    def plot_graph(self):
        self._plot_selected_cycles()
      
        for node in self.donor_patient_nodes:
            colour = '#97C2FC'
            if node.is_altruist:
                node_id = f"{node.donor.id}"
            else:
                node_id = f"{node.donor.id}, {node.patient.id}"
            if node_id not in self.added_nodes:
                if node_id in self.selected_nodes:
                    colour = '#faa7a7'
                self.graph.add_node(node_id, label=node_id, color=colour)
                self.added_nodes.add(node_id)
                
            for edge in node.out_edges:
                target_node = edge.donor_recipient_node
                colour = '#97C2FC'

                if not target_node.is_altruist:
                    target_node_id = f"{target_node.donor.id}, {target_node.patient.id}"

                    if target_node_id not in self.added_nodes:
                        if target_node_id in self.selected_nodes:
                            colour = '#faa7a7'
                        self.graph.add_node(target_node_id, label=target_node_id, color=colour)
                        self.added_nodes.add(target_node_id)
                    colour = '#97C2FC'
                    if (node_id, target_node_id) in self.selected_edges:
                        colour = '#faa7a7'
                    self.graph.add_edge(node_id, target_node_id, color=colour)

        net = Network(notebook=True, filter_menu=True, cdn_resources='remote', directed=True)
        net.repulsion()         
        net.show_buttons(filter_=['physics']) 
        net.from_nx(self.graph)
        net.write_html(f"./output/{self.solver_type}_full_graph.html")




