from typing import Callable, Dict, List
from core.tag import Tag
from core.block import BlockCollection, BlockState
import warnings

class StateTag(Tag):
	def __init__(self, tag:str, supplier:Callable[[], BlockCollection]):
		super().__init__(tag)
		self._supplier = supplier
		self._blockstates:List[BlockState] = []
	
	def add_state(self, state:Dict[str, str]):
		self._blockstates.append(BlockState(state))
		return self

	def get(self):
		base_results = self._supplier()

		result = BlockCollection()
		for state in self._blockstates:
			to_add = []
			for block in base_results:
				with_state = block.with_state(state)
				if not with_state:
					warnings.warn(f'Block eliminated because of conflicting state: {block}')
				to_add.append(with_state)
			result.insert(to_add)
		return result