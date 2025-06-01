# AI generated, then refined by sunnymax2002: https://chatgpt.com/share/683b706d-6f94-8008-9e7f-d259cbfbbca4
from pydantic import BaseModel, Field, TypeAdapter
from typing import List, Optional
from enum import Enum
from datetime import datetime
import networkx as nx
import yaml
import matplotlib.pyplot as plt

class RelationshipType(str, Enum):
    SUPPORTS = "supports"
    CHALLENGES = "challenges"
    UNDERLIES = "underlies"
    SOURCES = "sources"
    EVALUATES = "evaluates"
    CONNECTS_TO = "connects_to"
    INFERRED = "inferred"
    CONTRADICTS = "contradicts"  # New custom inference
    MEMBER_OF = "member_of"
    """Indicates a membership or belonging to a group or category"""

# TODO: Add docstrings from er_types.yaml
class EntityType(str, Enum):
    QUESTION = "Question"
    ANSWER = "Answer"
    FACT = "Fact"
    OPINION = "Opinion"
    CLAIM = "Claim"
    EVIDENCE = "Evidence"
    """Information that supports or refutes a claim"""
    ASSUMPTION = "Assumption"
    COUNTERARGUMENT = "Counterargument"
    REFERENCE = "Reference"
    SUBJECT = "Subject"
    OBJECT = "Object"
    ARGUMENT = "Argument"
    DOMAIN = "Domain"
    """A specific area of knowledge or expertise"""
    PRINCIPLE = "Principle"
    """A fundamental truth or proposition serving as the foundation for a system of belief or behavior"""
    TOPIC = "Topic"
    SUBTOPIC = "Subtopic"
    CONTEXT = "Context"
    INFERENCE = "Inference"
    PREMISE = "Premise"
    CONNECTION = "Connection"
    BIAS = "Bias"
    CONCLUSION = "Conclusion"
    METHODOLOGY = "Methodology"
    CRITERIA = "Criteria"
    FALLACY = "Fallacy"
    WEIGHT = "Weight"
    INSIGHT = "Insight"
    AUDIENCE = "Audience"
    STAKEHOLDER = "Stakeholder"
    TEMPORAL_CONTEXT = "TemporalContext"

class Metadata(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now) #TODO: (datetime.timezone.utc))
    updated_at: Optional[datetime] = None
    author: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

class Relationship(BaseModel):
    target_id: str
    type: RelationshipType
    description: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

class EntityHistoryEntry(BaseModel):
    version: int
    content: str
    metadata: Metadata

class Entity(BaseModel):
    id: str
    type: EntityType
    label: str
    # TODO: support different formats for content (e.g., text, markdown, HTML)
    # content can be a string, or a more complex structure like a dict or list, e.g., for rich text or structured data
    # for now, we keep it simple as a string
    content: Optional[str] = None
    metadata: Optional[Metadata] = None
    related_to: Optional[List[Relationship]] = []
    version: int = 1
    history: Optional[List[EntityHistoryEntry]] = []

class CriticalThinkingModel:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_entity(self, entity: Entity):
        if entity.id in self.graph:
            raise ValueError(f"Entity {entity.id} already exists.")
        
        # Validation: check related_to target_ids exist
        for rel in entity.related_to or []:
            if rel.target_id not in self.graph:
                raise ValueError(f"Target entity {rel.target_id} for relationship does not exist.")

        # TODO: add history also
        # TODO: assign a node color based on entity type
        self.graph.add_node(
            entity.id,
            label=entity.label,
            type=entity.type.value,
            content=entity.content,
            metadata=entity.metadata.model_dump() if entity.metadata else None,
            version=entity.version
        )
        for rel in entity.related_to or []:
            confidence = rel.confidence if rel.confidence is not None else 1.0
            self.graph.add_edge(
                entity.id,
                rel.target_id,
                type=rel.type.value,
                description=rel.description,
                confidence=confidence
            )

    def update_graph_from_yaml(self, yaml_path: str):
        # Load YAML file and parse entities
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
            # yaml_str = file.read()
        entities = TypeAdapter(List[Entity]).validate_python(data['entities'])
        for entity in entities:
            if entity.id in self.graph:
                # Update existing entity
                existing_data = self.graph.nodes[entity.id]
                existing_data.update(
                    label=entity.label,
                    type=entity.type.value,
                    content=entity.content,
                    metadata=entity.metadata.model_dump() if entity.metadata else None,
                    version=entity.version
                )
                self.graph.nodes[entity.id] = existing_data
            else:
                # Add new entity
                self.add_entity(entity)
        # Add relationships
        for entity in entities:
            for rel in entity.related_to or []:
                if self.graph.has_node(rel.target_id):
                    confidence = rel.confidence if rel.confidence is not None else 1.0
                    if not self.graph.has_edge(entity.id, rel.target_id):
                        self.graph.add_edge(
                            entity.id,
                            rel.target_id,
                            type=rel.type.value,
                            description=rel.description,
                            confidence=confidence
                        )

    def infer_new_links(self):
        inferred_edges = []

        # Transitive inferences
        for a, b, data_ab in self.graph.edges(data=True):
            for b2, c, data_bc in self.graph.edges(data=True):
                if b == b2:
                    conf_ab = data_ab.get('confidence', 1.0)
                    conf_bc = data_bc.get('confidence', 1.0)
                    inferred_conf = round(conf_ab * conf_bc, 2)

                    if data_ab['type'] == RelationshipType.SUPPORTS and data_bc['type'] == RelationshipType.SUPPORTS:
                        if not self.graph.has_edge(a, c):
                            inferred_edges.append((a, c, RelationshipType.INFERRED, f"Inferred SUPPORTS {a}->{b}->{c}", inferred_conf))
                    
                    if data_ab['type'] == RelationshipType.CHALLENGES and data_bc['type'] == RelationshipType.SUPPORTS:
                        if not self.graph.has_edge(a, c):
                            inferred_edges.append((a, c, RelationshipType.INFERRED, f"Inferred CHALLENGES {a}->{b}->{c}", inferred_conf))

        # Custom inference: SUPPORTS + CHALLENGES on same target → CONTRADICTS
        for node in self.graph.nodes():
            supports = [u for u, v, d in self.graph.in_edges(node, data=True) if d['type'] == RelationshipType.SUPPORTS]
            challenges = [u for u, v, d in self.graph.in_edges(node, data=True) if d['type'] == RelationshipType.CHALLENGES]
            for s in supports:
                for c in challenges:
                    if not self.graph.has_edge(s, c):
                        inferred_edges.append((s, c, RelationshipType.CONTRADICTS, f"Inferred CONTRADICTION: {s} supports {node} and {c} challenges {node}", 0.5))

        # Add inferred edges
        for a, c, rel_type, description, conf in inferred_edges:
            self.graph.add_edge(a, c, type=rel_type.value, description=description, confidence=conf)

        return inferred_edges

    def detect_cycles(self):
        try:
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                print("Detected cycles:")
                for cycle in cycles:
                    print(" -> ".join(cycle))
            else:
                print("No cycles detected.")
            return cycles
        except nx.NetworkXNoCycle:
            return []

    def export_graphml(self, filename):
        nx.write_graphml(self.graph, filename)
        print(f"Graph exported to {filename}")

    def import_graphml(self, filename):
        self.graph = nx.read_graphml(filename)
        print(f"Graph imported from {filename}")

    def get_partial_graph(self, anchor_id, depth=1):
        """
        Get a subgraph starting from the anchor node up to a specified depth.
        """
        if anchor_id not in self.graph:
            print(f"Anchor node '{anchor_id}' does not exist.")
            return None
        if depth < 1:
            print("Depth must be at least 1.")
            return None
        
        # Perform BFS to find nodes within the depth level
        visited = set()
        level = {anchor_id: 0}
        queue = [anchor_id]

        while queue:
            current = queue.pop(0)
            visited.add(current)
            current_level = level[current]

            if current_level < depth:
                for neighbor in self.graph.successors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        level[neighbor] = current_level + 1
        
        # Create subgraph
        subgraph = self.graph.subgraph(visited)

        return subgraph
        # # Visualization
        # pos = nx.spring_layout(subgraph)
        # labels = {node: f"{subgraph.nodes[node].get('type')} ({node})" for node in subgraph.nodes()}
        # edge_labels = {(u, v): f"{d['type']}" for u, v, d in subgraph.edges(data=True)}
        
        # plt.figure(figsize=(8, 6))
        # nx.draw(subgraph, pos, with_labels=True, labels=labels, node_color="lightgreen", node_size=1200, font_size=9)
        # nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels, font_color='red')
        # plt.title(f"Partial Graph from '{anchor_id}' up to depth {depth}")
        # plt.show()

    def visualize(self, graph: Optional[nx.DiGraph] = None):
        """
        Visualize the critical thinking model graph.
        If a specific graph is provided, visualize that instead of the main graph.
        """
        disp_graph = graph if graph is not None else self.graph
        pos = nx.spring_layout(disp_graph)
        labels = {node: f"{data.get('type')}: {data.get('label')}" for node, data in disp_graph.nodes(data=True)}
        edge_labels = {(u, v): f"{data.get('type')} ({data.get('confidence',1.0)})" for u, v, data in disp_graph.edges(data=True)}
        plt.figure(figsize=(10, 8))
        nx.draw(disp_graph, pos, with_labels=True, labels=labels, node_color="lightblue", node_size=1500, font_size=10)
        nx.draw_networkx_edge_labels(disp_graph, pos, edge_labels=edge_labels, font_color='red')
        plt.title("Critical Thinking Model")
        plt.show()

    def get_graph(self):
        return self.graph