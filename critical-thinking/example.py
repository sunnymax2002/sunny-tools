from model import CriticalThinkingModel, Entity, EntityType, Relationship, RelationshipType

model = CriticalThinkingModel()

# Add initial entities
model.add_entity(Entity(id="A", type=EntityType.EVIDENCE, label="Evidence A"))
model.add_entity(Entity(id="B", type=EntityType.CLAIM, label="Claim B", related_to=[
	Relationship(target_id="A", type=RelationshipType.SUPPORTS)
]))
model.add_entity(Entity(id="C", type=EntityType.COUNTERARGUMENT, label="Counter C", related_to=[
	Relationship(target_id="A", type=RelationshipType.CHALLENGES)
]))

# Inferences and export
inferred = model.infer_new_links()
print("Inferred edges:", inferred)

cycles = model.detect_cycles()
# TODO: model.export_graphml("critical_model.graphml")

# Import into a new model
# new_model = CriticalThinkingModel()
# TODO: new_model.import_graphml("critical_model.graphml")
model.visualize()

print('Done!')