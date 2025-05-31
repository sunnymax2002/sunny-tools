import yaml
from enum import Enum

# Function to load EntityType and RelationshipType from YAML
def load_types_from_yaml(yaml_file: str):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    # Dynamically create enums
    entity_types_dict = {list(item.keys())[0]: list(item.values())[0] for item in data['entity_types']}
    relationship_types_dict = {list(item.keys())[0]: list(item.values())[0] for item in data['relationship_types']}

    # Create dynamic Enums
    EntityType = Enum('EntityType', {key: key for key in entity_types_dict.keys()})
    RelationshipType = Enum('RelationshipType', {key: key for key in relationship_types_dict.keys()})

    return EntityType, RelationshipType, entity_types_dict, relationship_types_dict

# Load types
EntityType, RelationshipType, ENTITY_TYPE_DESCRIPTIONS, RELATIONSHIP_TYPE_DESCRIPTIONS = load_types_from_yaml(r"C:\Users\sunny\git_repos\sunny-tools\critical-thinking\er_types.yaml")