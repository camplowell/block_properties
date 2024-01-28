from __future__ import annotations
from core.blocks import Block

class BlockCollection:
	def __init__(self, blocks):
		self._contents = list(blocks)
	
	def __and__(self, other:BlockCollection):
		ret = []
		for a in self._contents:
			for b in other._contents:
				if a <= b:
					ret.append(a)
					break
				elif b <= a:
					ret.append(b)
					break
		return BlockCollection(ret)
	
	def __or__(self, other:BlockCollection):
		ret = self._contents
		for a in self._contents:
			for b in other._contents:
				if a >= b:
					ret.append(a)
					break
				elif b >= a:
					ret.append(b)
					break

		return BlockCollection(ret)

	def __repr__(self):
		return ' '.join(self._contents)