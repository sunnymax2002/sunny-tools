from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from uuid import uuid4
from datetime import datetime, timedelta
import json
from pathlib import Path

# Constants
QUEUE_NAMES = ["Urgent", "Current Focus", "Pipeline", "Someday or Never", "Archived"]
MAX_TASKS_PER_QUEUE = {
    "Urgent": 3,
    "Current Focus": 3
}
DATA_FILE = Path("storage.json")

# Models
class Level(str, Enum):
    HIGH = "High"
    LOW = "Low"

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: Optional[str] = ""
    impact: Level
    effort: Level
    tags: List[str] = []
    user: str
    owner: str
    status: int = Field(strict=True, le=100, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None

class TaskQueue(BaseModel):
    name: str
    tasks: List[Task] = []

# Task Manager
class TaskManager:
	def __init__(self):
		self.queues = self.load_queues()

	def load_queues(self) -> Dict[str, TaskQueue]:
		if not DATA_FILE.exists():
			return {name: TaskQueue(name=name) for name in QUEUE_NAMES}
		with open(DATA_FILE, "r") as f:
			raw = json.load(f)
			return {name: TaskQueue(**data) for name, data in raw.items()}

	def save_queues(self):
		with open(DATA_FILE, "w") as f:
			json.dump({name: queue.dict() for name, queue in self.queues.items()}, f, indent=2, default=str)

	def add_task(self, task: Task):
		now = datetime.utcnow()

		# Deadline logic
		if task.deadline:
			days_left = (task.deadline - now).days
			if days_left <= 3:
				if len(self.queues["Urgent"].tasks) < MAX_TASKS_PER_QUEUE["Urgent"]:
					self.queues["Urgent"].tasks.append(task)
					print(f"[ADD] Task '{task.title}' added to Urgent (deadline in {days_left} days)")
				else:
					print(f"[NOTICE] Urgent queue full. Task '{task.title}' added to Pipeline instead.")
					self.queues["Pipeline"].tasks.append(task)
				return
			else:
				self.queues["Pipeline"].tasks.append(task)
				print(f"[ADD] Task '{task.title}' added to Pipeline (future deadline)")
				return

		# Impact/Effort logic
		if task.effort == Level.HIGH and task.impact == Level.LOW:
			self.queues["Someday or Never"].tasks.append(task)
			print(f"[ADD] Task '{task.title}' added to Someday or Never")
		else:
			self.queues["Pipeline"].tasks.append(task)
			print(f"[ADD] Task '{task.title}' added to Pipeline")

	def list_tasks(self, user: str):
		for name, queue in self.queues.items():
			visible_tasks = [t for t in queue.tasks if t.user == user]
			if visible_tasks:
				print(f"\n== {name.upper()} ==")
				for task in visible_tasks:
					print(f"- {task.title} (ID: {task.id})")
					print(f"  Owner: {task.owner}, Status: {task.status}%, Due: {task.deadline}")
					print(f"  Impact: {task.impact}, Effort: {task.effort}, Tags: {', '.join(task.tags)}")

	def rescue_task_from_someday(self, tag_match: str, user: str):
		now = datetime.utcnow()
		rescued = []

		for task in list(self.queues["Someday or Never"].tasks):
			if task.user == user and tag_match in task.tags:
				self.queues["Someday or Never"].tasks.remove(task)

				if task.deadline and (task.deadline - now).days <= 3:
					if len(self.queues["Urgent"].tasks) < MAX_TASKS_PER_QUEUE["Urgent"]:
						self.queues["Urgent"].tasks.append(task)
						print(f"[RESCUE] '{task.title}' moved to Urgent (due soon)")
					else:
						self.queues["Pipeline"].tasks.append(task)
						print(f"[NOTICE] Urgent full. '{task.title}' moved to Pipeline")
				else:
					self.queues["Pipeline"].tasks.append(task)
					print(f"[RESCUE] '{task.title}' moved to Pipeline")
				rescued.append(task.title)

		if not rescued:
			print(f"[INFO] No tasks rescued with tag '{tag_match}' for user '{user}'")

	def refresh_due_tasks(self, current_user: str):
		now = datetime.utcnow()
		urgent_queue = self.queues["Urgent"]
		pipeline_queue = self.queues["Pipeline"]
		moved_count = 0
		follow_ups = []

		# 1. Auto-promote due tasks from Pipeline
		for task in list(pipeline_queue.tasks):
			if task.deadline:
				days_left = (task.deadline - now).days
				if days_left <= 3:
					if len(urgent_queue.tasks) >= MAX_TASKS_PER_QUEUE["Urgent"]:
						raise Exception(f"[BLOCKED] Cannot move '{task.title}' to Urgent. Queue is full.")
					pipeline_queue.tasks.remove(task)
					urgent_queue.tasks.append(task)
					moved_count += 1
					print(f"[AUTO-MOVE] Task '{task.title}' moved Pipeline → Urgent (due in {days_left} days)")

		if moved_count == 0:
			print("[CHECK] No tasks were promoted to Urgent.")

		# 2. Find delegated tasks needing follow-up
		for queue in self.queues.values():
			for task in queue.tasks:
				if (
					task.user == current_user and
					task.owner != current_user and
					task.status < 100 and
					(now - task.created_at).days > 4
				):
					follow_ups.append(task)

		if follow_ups:
			print(f"\n[DELEGATION FOLLOW-UP] You have {len(follow_ups)} delegated task(s) needing follow-up:")
			for t in follow_ups:
				print(f"- {t.title} (Owner: {t.owner}, Created: {t.created_at.date()}, Status: {t.status}%)")
		else:
			print("[DELEGATION] No overdue delegated tasks found.")


	def save(self):
		self.save_queues()
        
# Usage

# from task_manager import Task, Level, TaskManager
from datetime import datetime, timedelta

manager = TaskManager()
user = "alice"

# Add a task with deadline within 3 days
urgent_task = Task(
    title="Fix security bug",
    description="Critical CVE",
    impact=Level.HIGH,
    effort=Level.LOW,
	status=0,
    tags=["security", "urgent"],
    user=user,
    owner=user,
    deadline=datetime.utcnow() + timedelta(days=2)
)
manager.add_task(urgent_task)

# Add a someday task
someday_task = Task(
    title="Refactor old reports",
    description="Low priority rewrite",
    impact=Level.LOW,
    effort=Level.HIGH,
	status=0,
    tags=["refactor", "report"],
    user=user,
    owner=user
)
manager.add_task(someday_task)

# Rescue based on tag
manager.rescue_task_from_someday("report", user)

manager.save()
manager.list_tasks(user)

# Periodic scan example
try:
    manager.refresh_due_tasks()
except Exception as e:
    print(f"[ERROR] {e}")