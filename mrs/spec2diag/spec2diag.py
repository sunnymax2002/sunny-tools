import yaml
from graphviz import Digraph

def load_system_spec(yaml_file):
    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)

def create_block_diagram(system_spec, output_file=r"C:\Users\sunny\git_repos\sunny-tools\mrs\spec2diag\block_diagram"):
    layout = system_spec.get('layout', {})
    direction = layout.get('direction', 'TB')

    dot = Digraph(format='png')
    dot.attr(rankdir=direction)
    dot.graph_attr['splines'] = 'ortho'

    # Add nodes with attributes
    for block in system_spec.get('blocks', []):
        node_id = block['id']
        label = block.get('label', node_id)
        attrs = {
            'label': label,
            'shape': block.get('shape', 'box'),
            'style': block.get('style', 'solid'),
            'color': block.get('color', 'black'),
        }
        dot.node(node_id, **attrs)

    # Add connections with labels
    for conn in system_spec.get('connections', []):
        dot.edge(conn['from'], conn['to'], label=conn.get('label', ''))

    dot.render(output_file, cleanup=True)
    print(f"Diagram saved to {output_file}.png")

if __name__ == "__main__":
    spec = load_system_spec(r"C:\Users\sunny\git_repos\sunny-tools\mrs\spec2diag\system.yaml")
    create_block_diagram(spec)
