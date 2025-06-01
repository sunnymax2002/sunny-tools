from model import CriticalThinkingModel, Entity, EntityType, Relationship, RelationshipType
# from gui_pyqt5 import launch_gui
from gui_pyvis import export_to_pyvis
from pathlib import Path
    
def load_model_from_yaml(yaml_dir):
	for path in Path(yaml_dir).rglob('*.yaml'):
          print(path.name)
        
def build_sample_model():
    model = CriticalThinkingModel()
    # model.add_entity(Entity("A", EntityType.FACT, "Strong brand."))
    # model.add_entity(Entity("B", EntityType.CLAIM, "Brand supports pricing power.", [Relationship("A", RelationshipType.SUPPORTS)]))
    # model.add_entity(Entity("C", EntityType.CONCLUSION, "Company has moat.", [Relationship("B", RelationshipType.UNDERLIES)]))
    
	# Fetch all YAML files in the directory
    yaml_dir = r"C:\Users\sunny\git_repos\sunny-data\finance\investing\critical-thinking"
    for path in Path(yaml_dir).rglob('*.yaml'):
        model.update_graph_from_yaml(path)    
    
    return model

if __name__ == "__main__":
    model = build_sample_model()
    mode = "2" # TODO: input("Choose visualization mode (1=PyQt5, 2=PyVis): ")
    
	# TODO: Filter a subgraph and provide to PyVis
    if mode == "1":
        print("Unsupported mode. Please use PyVis for now.")
        # launch_gui(model)
    elif mode == "2":
        export_to_pyvis(model, "critical_thinking_graph.html")
        print("Open 'critical_thinking_graph.html' in your browser.")
    else:
        print("Invalid mode.")
