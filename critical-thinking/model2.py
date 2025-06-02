from typing import Dict, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
import networkx as nx

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
import networkx as nx
import pandas as pd
from pydantic import ValidationError

# --- Core Entities (same as before) ---
class Reference(BaseModel):
    id: str
    title: str
    url: Optional[HttpUrl] = None
    authors: Optional[List[str]] = None
    publication_year: Optional[int] = None

class Fact(BaseModel):
    id: str
    statement: str
    reference_ids: Optional[List[str]] = None

class Claim(BaseModel):
    id: str
    statement: str
    fact_ids: List[str]
    reference_ids: Optional[List[str]] = None

class Opinion(BaseModel):
    id: str
    statement: str
    justification: Optional[str] = None
    reference_ids: Optional[List[str]] = None

class ReasoningStep(BaseModel):
    description: str
    claim_ids: Optional[List[str]] = None
    fact_ids: Optional[List[str]] = None
    opinion_ids: Optional[List[str]] = None

class Argument(BaseModel):
    id: str
    claim: Optional[str]
    claim_ids: Optional[List[str]] = None
    reasoning_steps: List[ReasoningStep]
    reference_ids: Optional[List[str]] = None

class QuestionSequenceCondition(BaseModel):
    based_on_question_id: str
    condition_description: str

class QuestionConnection(BaseModel):
    connection_type: str
    target_question_id: str
    condition: Optional[QuestionSequenceCondition] = None

class Question(BaseModel):
    id: str
    question_text: str
    fact_ids: Optional[List[str]] = None
    opinion_ids: Optional[List[str]] = None
    claim_ids: Optional[List[str]] = None
    reference_ids: Optional[List[str]] = None
    connections: Optional[List[QuestionConnection]] = None

class Answer(BaseModel):
    id: str
    content: str
    argument_ids: List[str]
    reference_ids: Optional[List[str]] = None

class Topic(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    question_ids: Optional[List[str]] = None

class Subject(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    topic_ids: Optional[List[str]] = None

class ChecklistTemplate(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    topic_ids: List[str]
    reference_ids: Optional[List[str]] = None

class ChecklistInstance(BaseModel):
    id: str
    template_id: str
    target_context: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    question_answers: Dict[str, str] = {}

# --- CriticalThinkingDatabase with optimized storage ---
class CriticalThinkingDatabase(BaseModel):
    references: Dict[str, Reference] = Field(default_factory=dict)
    facts: Dict[str, Fact] = Field(default_factory=dict)
    claims: Dict[str, Claim] = Field(default_factory=dict)
    opinions: Dict[str, Opinion] = Field(default_factory=dict)
    arguments: Dict[str, Argument] = Field(default_factory=dict)
    questions: Dict[str, Question] = Field(default_factory=dict)
    answers: Dict[str, Answer] = Field(default_factory=dict)
    topics: Dict[str, Topic] = Field(default_factory=dict)
    subjects: Dict[str, Subject] = Field(default_factory=dict)
    checklist_templates: Dict[str, ChecklistTemplate] = Field(default_factory=dict)
    checklist_instances: Dict[str, ChecklistInstance] = Field(default_factory=dict)
    graph: nx.DiGraph = Field(default_factory=nx.DiGraph)

    class Config:
        arbitrary_types_allowed = True

    # --- Generic CRUD methods ---
    def _add_entity(self, entity, collection_name: str):
        collection: Dict[str, BaseModel] = getattr(self, collection_name)
        collection[entity.id] = entity
        self.graph.add_node(entity.id, type=collection_name[:-1], data=entity)
        self._add_entity_edges(entity)

    def _get_entity(self, collection_name: str, entity_id: str):
        collection: Dict[str, BaseModel] = getattr(self, collection_name)
        return collection.get(entity_id)

    def _update_entity(self, collection_name: str, entity):
        collection: Dict[str, BaseModel] = getattr(self, collection_name)
        if entity.id not in collection:
            raise ValueError(f"{collection_name[:-1].capitalize()} with id {entity.id} not found")
        collection[entity.id] = entity
        self.graph.nodes[entity.id]['data'] = entity
        self._remove_entity_edges(entity.id)
        self._add_entity_edges(entity)

    def _delete_entity(self, collection_name: str, entity_id: str):
        collection: Dict[str, BaseModel] = getattr(self, collection_name)
        if entity_id in collection:
            del collection[entity_id]
        if self.graph.has_node(entity_id):
            self.graph.remove_node(entity_id)

    def _add_entity_edges(self, entity):
        # Same as before; establish edges based on entity relationships
        if isinstance(entity, Fact) and entity.reference_ids:
            for ref_id in entity.reference_ids:
                self.graph.add_edge(entity.id, ref_id, relation='supported_by')
        if isinstance(entity, Claim):
            for fact_id in entity.fact_ids:
                self.graph.add_edge(entity.id, fact_id, relation='supported_by')
            if entity.reference_ids:
                for ref_id in entity.reference_ids:
                    self.graph.add_edge(entity.id, ref_id, relation='supported_by')
        if isinstance(entity, Opinion) and entity.reference_ids:
            for ref_id in entity.reference_ids:
                self.graph.add_edge(entity.id, ref_id, relation='supported_by')
        if isinstance(entity, Argument):
            if entity.claim_ids:
                for claim_id in entity.claim_ids:
                    self.graph.add_edge(entity.id, claim_id, relation='supports')
            for step in entity.reasoning_steps:
                for fid in step.fact_ids or []:
                    self.graph.add_edge(entity.id, fid, relation='uses')
                for oid in step.opinion_ids or []:
                    self.graph.add_edge(entity.id, oid, relation='uses')
                for cid in step.claim_ids or []:
                    self.graph.add_edge(entity.id, cid, relation='uses')
            if entity.reference_ids:
                for ref_id in entity.reference_ids:
                    self.graph.add_edge(entity.id, ref_id, relation='supported_by')
        if isinstance(entity, Question):
            for fid in entity.fact_ids or []:
                self.graph.add_edge(entity.id, fid, relation='related_to')
            for oid in entity.opinion_ids or []:
                self.graph.add_edge(entity.id, oid, relation='related_to')
            for cid in entity.claim_ids or []:
                self.graph.add_edge(entity.id, cid, relation='related_to')
            for ref_id in entity.reference_ids or []:
                self.graph.add_edge(entity.id, ref_id, relation='supported_by')
            for conn in entity.connections or []:
                self.graph.add_edge(entity.id, conn.target_question_id, relation=conn.connection_type)
        if isinstance(entity, Topic) and entity.question_ids:
            for qid in entity.question_ids:
                self.graph.add_edge(entity.id, qid, relation='contains')
        if isinstance(entity, Subject) and entity.topic_ids:
            for tid in entity.topic_ids:
                self.graph.add_edge(entity.id, tid, relation='contains')
        if isinstance(entity, ChecklistTemplate) and entity.topic_ids:
            for tid in entity.topic_ids:
                self.graph.add_edge(entity.id, tid, relation='includes')
        if isinstance(entity, ChecklistInstance):
            self.graph.add_edge(entity.id, entity.template_id, relation='instance_of')
            for qid, aid in entity.question_answers.items():
                self.graph.add_edge(entity.id, qid, relation='answered')
                self.graph.add_edge(qid, aid, relation='answered_with')

    def _remove_entity_edges(self, entity_id):
        edges_to_remove = list(self.graph.out_edges(entity_id)) + list(self.graph.in_edges(entity_id))
        self.graph.remove_edges_from(edges_to_remove)

    # --- Specific CRUD for Reference ---
    def add_reference(self, reference: Reference):
        self._add_entity(reference, 'references')
    def get_reference(self, reference_id: str) -> Optional[Reference]:
        return self._get_entity('references', reference_id)
    def update_reference(self, reference: Reference):
        self._update_entity('references', reference)
    def delete_reference(self, reference_id: str):
        self._delete_entity('references', reference_id)

    # TODO: Similarly, CRUD methods can be created for other entity types...

    # Mapping from entity_type string to model class and collection name
    _entity_map = {
        "Reference": (Reference, "references"),
        "Fact": (Fact, "facts"),
        "Claim": (Claim, "claims"),
        "Opinion": (Opinion, "opinions"),
        "Argument": (Argument, "arguments"),
        "Question": (Question, "questions"),
        "Answer": (Answer, "answers"),
        "Topic": (Topic, "topics"),
        "Subject": (Subject, "subjects"),
        "ChecklistTemplate": (ChecklistTemplate, "checklist_templates"),
        "ChecklistInstance": (ChecklistInstance, "checklist_instances"),
    }

    def import_entities_from_csv(self, entity_type: str, csv_path: str) -> int:
        """
        Import entities from CSV file into the database.
        
        Args:
            entity_type: The entity type as string (e.g., 'Reference', 'Fact', 'Claim').
            csv_path: Path to the CSV file.
        
        Returns:
            Number of successfully imported entities.
        """
        if entity_type not in self._entity_map:
            raise ValueError(f"Unknown entity_type '{entity_type}'. Valid types: {list(self._entity_map.keys())}")

        model_cls, collection_name = self._entity_map[entity_type]

        # Read CSV
        df = pd.read_csv(csv_path)

        # Get valid fields for the model
        valid_fields = set(model_cls.model_fields.keys()) if hasattr(model_cls, 'model_fields') else set(model_cls.__fields__.keys())

        # Filter dataframe columns to only valid fields
        filtered_df = df[[col for col in df.columns if col in valid_fields]]

        count = 0
        for idx, row in filtered_df.iterrows():
            try:
                entity = model_cls(**row.dropna().to_dict())
                self._add_entity(entity, collection_name)
                count += 1
            except ValidationError as e:
                print(f"Skipping row {idx} due to validation error: {e}")

        return count
