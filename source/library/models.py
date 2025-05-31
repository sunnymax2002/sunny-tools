from __future__ import annotations
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

# TODO: Consider using Treelib: https://treelib.readthedocs.io/en/latest/
class Tag(BaseModel):
	label: str
	parent: str = ""

	@classmethod
	def getHierName(cls, et: Tag) -> str:
		qualifier = ':' + et.label
		if et.parent is None:
			return qualifier
		return Tag.getHierName(et.parent) + qualifier

class Information(BaseModel):
	"""
	Information is a general model for any piece of information, such as a question, answer, or fact.
	It can be used to represent various types of information in a structured way.
	"""
	# id is used to map different instances of Information, e.g., a question to an answer
	id: str
	title: str
	description: str = ""
	# multiple tags can be applied, and tags have hierarchy. In some cases, tags can be inferred, e.g., tags of an answer can be inferred from the mapped question through id
	tags: List[str] = []
	type: str
	# url (http(s):// or file:// in general)
	url: str = ""
	# location indicates page, line number within a document, e.g. pdf, may not be relevant for http urls
	location: str = ""
	props: dict = {}

class Fact(Information):
	"""
	Fact is a specific type of Information that represents a piece of knowledge or data.
	It can be used to store factual information in a structured way.
	"""
	pass

class Question(Information):
	"""
	Question is a specific type of Information that represents a question.
	It can be used to represent various types of questions in a structured way.
	"""
	pass

class Answer(Information):
	"""
	Answer is a specific type of Information that represents an answer to a question.
	It can be used to represent various types of answers in a structured way.
	"""
	# the ID of the question this answer is related to
	# this allows for linking answers to their corresponding questions
	# and enables better organization and retrieval of information
	question_id: str = ""
	# the ID of the fact this answer is related to
	fact_id: str = ""

class Document(Information):
	"""
	Document is a specific type of Information that represents a document.
	It can be used to represent various types of documents in a structured way.
	"""
	pass

class Topic(Information):
	"""
	Topic is a specific type of Information that represents a topic.
	It can be used to represent various types of topics in a structured way.
	"""
	pass

# 