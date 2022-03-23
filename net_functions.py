import networkx as nx


def is_graph_acyclic(semantic_net, relation_id):

    G = nx.DiGraph()

    added_nodes = set()

    for rel in semantic_net.select_relations(relation_id, None, None):
        source_node = rel.source_obj.id
        target_node = rel.target_obj.id

        if source_node not in added_nodes:
            G.add_node(source_node)
            added_nodes.add(source_node)

        if target_node not in added_nodes:
            G.add_node(target_node)
            added_nodes.add(target_node)

        G.add_edge(source_node, target_node)

    is_acyclic = len(list(nx.simple_cycles(G))) == 0

    return is_acyclic
