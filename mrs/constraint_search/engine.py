from pydantic import BaseModel

import re
import yaml
from typing import Any, Dict, List, Tuple, Union


def get_nested_attr(obj: Any, path: str) -> Any:
    """Access nested attributes using dot notation."""
    for part in path.split("."):
        obj = getattr(obj, part, None)
        if obj is None:
            return None
    return obj


def fuzzy_match(value: str, pattern: str) -> bool:
    return isinstance(value, str) and pattern.lower() in value.lower()


def evaluate_single_constraint(value: Any, op: str, expected: Any) -> bool:
    ops = {
        "$eq": lambda a, b: a == b,
        "$ne": lambda a, b: a != b,
        "$gt": lambda a, b: a > b,
        "$gte": lambda a, b: a >= b,
        "$lt": lambda a, b: a < b,
        "$lte": lambda a, b: a <= b,
        "$in": lambda a, b: a in b if isinstance(b, list) else False,
        "$regex": lambda a, b: bool(re.search(b, a)) if isinstance(a, str) else False,
    }
    return ops.get(op, lambda a, b: False)(value, expected)


def evaluate_constraint(value: Any, constraint: Any) -> float:
    """
    Evaluate constraint and return weighted match score.
    """
    if not isinstance(constraint, dict):
        return 1.0 if value == constraint else 0.0

    weight = constraint.get("$weight", 1.0)
    score = 0.0
    total_conditions = 0

    for op, expected in constraint.items():
        if op == "$weight":
            continue
        total_conditions += 1
        if op == "$fuzzy":
            if fuzzy_match(value, expected):
                score += 1.0
        elif evaluate_single_constraint(value, op, expected):
            score += 1.0

    if total_conditions == 0:
        return 0.0
    return (score / total_conditions) * weight


def search_and_rank_models(
    model_dict: Dict[str, Dict[str, BaseModel]],
    yaml_constraints: str
) -> List[Tuple[BaseModel, float]]:
    """
    Search and rank Pydantic model instances based on constraints in YAML format.

    Args:
        model_dict: Dictionary of model name -> {instance_id: model instance}
        yaml_constraints: YAML string with constraint structure

    Returns:
        List of (instance, score)
    """
    constraint_dict = yaml.safe_load(yaml_constraints)
    ranked_results: List[Tuple[BaseModel, float]] = []

    for model_name, model_spec in constraint_dict.items():
        attr_constraints = model_spec.get("constraints", {})
        count = model_spec.get("count", 1)

        instances = model_dict.get(model_name, {})
        scored_instances: List[Tuple[float, BaseModel]] = []

        for instance in instances.values():
            total_score = sum(
                evaluate_constraint(get_nested_attr(instance, attr), constraint)
                for attr, constraint in attr_constraints.items()
            )
            if total_score > 0:
                scored_instances.append((total_score, instance))

        # Sort descending by score
        scored_instances.sort(reverse=True, key=lambda x: x[0])
        ranked_results.extend((inst, score) for score, inst in scored_instances[:count])

    return ranked_results

def format_search_results_markdown(
    results: List[Tuple[BaseModel, float]],
    constraint_yaml: str
) -> str:
    constraint_dict = yaml.safe_load(constraint_yaml)
    grouped: Dict[str, List[Tuple[BaseModel, float]]] = {}

    for instance, score in results:
        model_name = type(instance).__name__
        grouped.setdefault(model_name, []).append((instance, score))

    lines = []

    for model_name, matches in grouped.items():
        lines.append(f"## 🔍 Model: `{model_name}`\n")
        lines.append("| # | Instance | Score | " + " | ".join(constraint_dict.get(model_name, {}).get("constraints", {}).keys()) + " |")
        lines.append("|---|----------|-------|" + "|".join(["---"] * len(constraint_dict.get(model_name, {}).get("constraints", {}))) + "|")

        for i, (instance, score) in enumerate(matches, start=1):
            constraint_attrs = constraint_dict.get(model_name, {}).get("constraints", {})
            values = [str(get_nested_attr(instance, attr)) for attr in constraint_attrs]
            lines.append(f"| {i} | `{repr(instance)}` | {score:.2f} | " + " | ".join(values) + " |")

        lines.append("")  # Extra newline between models

    return "\n".join(lines)


class Profile(BaseModel):
    name: str

class User(BaseModel):
    id: int
    profile: Profile
    age: int

class Product(BaseModel):
    id: int
    title: str
    price: float

data = {
    "User": {
        "u1": User(id=1, profile=Profile(name="Alice"), age=30),
        "u2": User(id=2, profile=Profile(name="Bob"), age=25),
        "u3": User(id=3, profile=Profile(name="Alicia"), age=23),
    },
    "Product": {
        "p1": Product(id=1, title="Notebook", price=10.0),
        "p2": Product(id=2, title="Pen", price=2.5),
    }
}

yaml_constraints = """
User:
  count: 2
  constraints:
    profile.name:
      $fuzzy: ali
      $weight: 2.0
    age:
      $gt: 20
      $lt: 30
      $weight: 1.0

Product:
  count: 1
  constraints:
    price:
      $lte: 10.0
    title:
      $regex: "^Note.*"
"""

results = search_and_rank_models(data, yaml_constraints)

for instance, score in results:
    print(f"{instance} -> score: {score:.2f}")
