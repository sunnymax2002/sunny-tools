from pyvis.network import Network

def export_to_pyvis(model, filename="critical_thinking_graph.html"):
    net = Network(height="750px", width="100%", directed=True, notebook=False)
    G = model.graph
    for node, data in G.nodes(data=True):
        net.add_node(node, label=data.get("label", node), title=data.get("content", ""), group=str(data.get("type", "")))
    # TODO: Hidden edges to represent 
    for u, v, data in G.edges(data=True):
        net.add_edge(u, v, title=f"{data.get('type')} ({data.get('confidence',1.0)})")
    net.show_buttons(filter_=['physics'])
    net.show(filename, notebook=False)