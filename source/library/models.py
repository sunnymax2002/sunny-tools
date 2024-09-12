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

class Information:
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