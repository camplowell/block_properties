from __future__ import annotations
import csv
from dataclasses import dataclass, field
from pathlib import Path
import shutil
from typing import Dict, Iterable
import warnings

from core.block import Block, BlockCollection

@dataclass(init=True, repr=True)
class _Node:
	tag:Tag|None = None
	children:Dict[str, _Node] = field(default_factory=dict)

class TagLibrary:
	def __init__(self, folder:Path = None):
		self.folder = Path(folder) if folder else None
		self._root = _Node()
	
	def get(self, tag:str):
		node = self._get_node(tag, create=bool(self.folder))
		if node.tag:
			return node.tag
		folder = self._get_folder(tag)
		if not folder or not folder.exists():
			raise ValueError(f'No such tag: {tag}')
		if folder.joinpath('_bool.tsv').exists():
			return self.create_bool(tag)
		else:
			return self.create_enum(tag, [])
	
	def delete(self, tag:str):
		node = self._get_node(tag, create=bool(self.folder))
		if self.folder:
			tag_ = self.get(tag)
			tag_.delete()
		node.tag = None
	
	def create_bool(self, tag:str):
		node = self._get_node(tag, create=True)
		node.tag = BoolTag(tag, self)
		return node.tag
	
	def create_enum(self, tag:str, values:Iterable[str]):
		node = self._get_node(tag, create=True)
		node.tag = EnumTag(tag, self, values=values)
		return node.tag
	
	def register_mixin(self, mixin:Tag):
		node = self._get_node(str(mixin), create=True)
		if node.tag:
			warnings.warn(f'Overriding existing tag {str(mixin)} with mixin!')
		node.tag = mixin
		mixin._library = self
	
	def _get_node(self, tag:str, create=False):
		here = self._root
		for part in tag.split('/'):
			if part not in here.children:
				if create:
					here.children[part] = _Node()
				else:
					raise ValueError(f'No such tag: {tag}')
			here = here.children[part]
		return here
	
	def _get_folder(self, tag:str|Tag):
		if self.folder:
			return self.folder.joinpath(str(tag))
		return None

class Tag:
	def __init__(self, tag:str, library:TagLibrary = None):
		self._tag = tag
		self._library = library
	
	def parent(self):
		if '/' not in self._tag:
			return None
		return self._library.get(self._tag[:self._tag.rfind('/')])

	def get(self) -> BlockCollection:
		if type(self) is Tag:
			raise ValueError('Tried to call get on a generic Tag.')
		raise NotImplementedError(f'Subclass {type(self)} is missing a get method!')
	
	def __repr__(self):
		return self._tag
	
	def _file(self, key:str):
		if not self._library.folder:
			return None
		return self._library._get_folder(self._tag).joinpath(f'{str(key)}.tsv')
	
	def _load_file(self, key:str):
		file = self._file(key)
		if file is None:
			return None
		output = BlockCollection()
		with file.open('r') as stream:
			for line in csv.reader(stream, delimiter='\t'):
				output.insert(BlockCollection.from_strings(line))
		return output

	def _save_file(self, key:str, blocks:BlockCollection):
		file:Path = self._file(key)
		if file is None:
			raise RuntimeError('Cannot save state to disk in a memory-only library!')
		file.parent.mkdir(exist_ok=True)
		with file.open('w') as stream:
			stream.write('\n'.join([repr(block) for block in blocks]))
	
	def _delete(self):
		folder = self._library._get_folder(self)
		if not folder:
			raise RuntimeError('Cannot remove state from disk in a memory-only library!')
		shutil.rmtree(folder.absolute())

class BoolTag(Tag):
	_KEY = '_bool'
	def __init__(self, tag:str, library:TagLibrary):
		super().__init__(tag, library)
		self._contents:BlockCollection = None
	
	def get(self):
		self._load()
		return self._contents.copy()
	
	def add(self, blocks:Iterable[Block]):
		if self.parent():
			self.parent().add(blocks)
		self._load()
		self._contents.insert(blocks)
	
	def remove(self, blocks:Iterable[Block]):
		self._load()
		self._contents.remove(blocks)
	
	def _load(self):
		if self._contents is None:
			self._contents = self._load_file(self._KEY) or BlockCollection()

	def save(self):
		self._save_file(self._KEY, self._contents or BlockCollection())
	
	def delete(self):
		self._delete()

class EnumTag(Tag):
	def __init__(self, tag:str, library:TagLibrary, values:Iterable[str]):
		super().__init__(tag, library)
		self._contents:Dict[str, BlockCollection] = dict()
		self._edited = set()
		for value in set(values):
			self._contents[value] = None
	
	def get(self, value:str=...):
		if value is ...:
			result = BlockCollection()
			for val in self.values:
				result.insert(self.get(val))
			return result
		
		if value not in self._contents or self._contents[value] is None:
			loaded = self._load_file(value)
			if loaded is None:
				if value in self._contents:
					self._contents[value] = BlockCollection()
				else:
					raise ValueError(f'The tag {self} has no value "{value}"')
			self._contents[value] = loaded
		return self._contents[value].copy()
	
	def add(self, value:str, blocks:Iterable[Block]):
		if value not in self._contents:
			raise ValueError(f'Enum tag {self} has no value "{value}"')
		self._contents[value].insert(blocks)
		self._edited.add(value)
	
	def remove(self, value:str, blocks:Iterable[Block]):
		if value not in self._contents:
			raise ValueError(f'Enum tag {self} has no value "{value}"')
		self._contents[value].remove(blocks)
		self._edited.add(value)
	
	def add_value(self, value:str):
		if value in self._contents:
			raise ValueError(f'Enum tag {self} already has the value "{value}"')
		self._contents[value] = BlockCollection()
		self._edited.add(value)

	def remove_value(self, value:str):
		if value not in self._contents:
			raise ValueError(f'Enum tag {self} has no value "{value}"')
		del self._contents[value]
		self._edited.add(value)
	
	def save(self):
		if not self._library.folder:
			raise RuntimeError(f'Cannot save memory-only tag {self}')
		for value in self._edited:
			if value in self._contents: # Modified contents
				self._save_file(value, self._contents[value] or BlockCollection())
			else:
				self._file(value).unlink()
	
	def delete(self):
		self._delete()