from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Iterable, Set

class BlockState:
	def __init__(self, state:Dict[str, Set[str]]):
		self._dict:Dict[str, FrozenSet[str]] = dict()
		for key in sorted(state.keys()):
			self._dict[key] = frozenset(sorted(state[key]))
		self._hash = None
	
	def items(self):
		return self._dict.items()
	def keys(self):
		return self._dict.keys()
	def values(self):
		return self._dict.values()
	def __iter__(self):
		return iter(self._dict)
	def __len__(self):
		return len(self._dict)
	def __getitem__(self, key):
		return self._dict[key]
	
	def isParentOf(self, other:BlockState):
		for key, value in self.items():
			if key not in other:
				return False
			if not other[key] <= value:
				return False
		return True
	
	def isChildOf(self, other:BlockState):
		return other.isParentOf(self)

@dataclass(init=True, frozen=True)
class Block:
	namespace:str
	name:str
	state:BlockState
	
	@classmethod
	def from_str(cls, block:str):
		parts = block.split(':')
		state = dict()
		while '=' in parts[-1]:
			key, vals = parts.pop().split('=')
			vals = vals.split(',')
			state[key] = set(vals)
		
		name = parts.pop()
		namespace = parts[0] if parts else "minecraft"
		return Block(namespace, name, BlockState(state))
	
	def copy(self):
		return Block(self.namespace, self.name, self.state)
	
	def with_state(self, state:Dict[str, Iterable[str]]):
		"""Return a copy of this block with additional blockstate.
		
		Returns None if the given blockstate conflicts with existing state."""
		new_state = self._intersect_state(state)
		if new_state is None:
			return None
		return Block(self.namespace, self.name, new_state)
	
	def without_state(self, state:BlockState):
		if self.state.isChildOf(state):
			return None
		new_state = dict()
		for key, value in self.state.items():
			if key not in state or state[key].issuperset(value):
				new_state[key] = value
				continue
			difference = value.difference(state[key])
			if difference:
				new_state[key] = difference
		return Block(self.namespace, self.name, BlockState(new_state))

	def isParentOf(self, other:Block):
		if not isinstance(other, Block):
			raise ValueError("Cannot compare a Block to a {}".format(type(other)))
		if self.namespace != other.namespace or self.name != other.name:
			return False
		return self.state.isParentOf(other.state)
	
	def isChildOf(self, other:Block):
		return other.isParentOf(self)
	
	def intersect(self, other:Block):
		if self.namespace != other.namespace or self.name != other.name:
			return None
		intersected_state = self._intersect_state(other.state)
		if intersected_state is None:
			return None
		return Block(self.namespace, self.name, intersected_state)
	
	def same_base(self, other:Block):
		return self.namespace == other.namespace and self.name == other.name
	
	def _intersect_state(self, state:Dict[str, Iterable[str]]):
		fulldict = dict()
		keys = set(self.state.keys()).union(state.keys())
		for key in keys:
			if (key in self.state) and (key in state):
				value_overlap = set(self.state[key]).intersection(state[key])
				if not value_overlap:
					return None
				fulldict[key] = value_overlap
			else:
				fulldict[key] = self.state[key] if key in self.state else set(state[key])
		return BlockState(fulldict)
	
	def __eq__(self, other:Block):
		if not isinstance(other, Block):
			return False
		return (
			self.namespace == other.namespace and
			self.name == other.name and
			self.state == other.state
		)

	def __le__(self, other):
		return self.isChildOf(other)
	
	def __ge__(self, other):
		return self.isParentOf(other)
	
	def __and__(self, other):
		return self.intersect(other)
	
	def __repr__(self):
		return str(self)
	
	def __str__(self):
		parts = [self.namespace, self.name]
		parts.extend([f'{key}={",".join(value)}' for key, value in self.state.items()])
		return ':'.join(parts)
	
	def __hash__(self) -> int:
		return hash(repr(self))
	
	def __eq__(self, other):
		if not isinstance(other, Block):
			return False
		return repr(self) == repr(other)

class BlockCollection(Iterable[Block]):
	def __init__(self, contents:Iterable[Block] = [], verify = False):
		self._contents:List[Block] = []
		if not contents:
			return
		if verify:
			self.insert(self, contents)
		else:
			self._contents.extend(contents)
	@classmethod
	def from_strings(cls, blocks:Iterable[str]):
		return BlockCollection([Block.from_str(item) for item in blocks])

	def copy(self):
		return BlockCollection(self._contents)

	def insert(self, blocks):
		"""Add the given blocks to this BlockCollection."""
		for obj in blocks:
			if obj:
				self._add(obj)
		return self
	
	def remove(self, blocks):
		"""Remove the given blocks from this BlockCollection."""
		for block in blocks:
			self._discard(block)
		return self
	
	def union(self, blocks):
		"""Return a copy of this BlockCollection but with the given blocks."""
		return self.copy().insert(blocks)
	
	def difference(self, blocks):
		"""Return a copy of this BlockCollection but without the given blocks."""
		return self.copy().remove(blocks)
	
	def intersection(self, blocks):
		"""Return a new BlockCollection with only the blocks that are in both collections."""
		result = []
		for mine in self._contents:
			for theirs in blocks:
				intersect = mine & theirs
				if intersect and intersect not in result:
					result.append(intersect)
		return BlockCollection(result)
	
	def _add(self, block:Block):
		for i, existing in enumerate(self._contents):
			if block >= existing:
				self._contents[i] = block
				return
			if block <= existing:
				return
		self._contents.append(block)
	
	def _discard(self, block:Block):
		filtered = []
		for existing in self._contents:
			if existing.isChildOf(block):
				continue
			if existing.same_base(block):
				existing = existing.without_state(block.state)
			if existing:
				filtered.append(existing)
		self._contents = filtered

	def __iter__(self):
		return iter(self._contents)
	
	def __add__(self, other:Iterable[Block]):
		return self.union(other)
	
	def __sub__(self, other:Iterable[Block]):
		return self.difference(other)
	
	def __mul__(self, other:Iterable[Block]):
		return self.intersection(other)
	
	def __len__(self):
		return len(self._contents)
	
	def __repr__(self):
		return ' '.join([str(block) for block in self._contents])
	
	def __str__(self):
		return f'{" ".join([str(block) for block in self._contents[:4]])}{"..." if len(self._contents) > 4 else ""} ({len(self._contents)} items)'
	
	def __eq__(self, other):
		if not isinstance(other, BlockCollection):
			return False
		return frozenset(self._contents) == frozenset(other._contents)
	
	def __bool__(self):
		return bool(self._contents)