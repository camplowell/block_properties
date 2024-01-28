from __future__ import annotations

class Block:
	def __init__(self, block:str):
		if isinstance(block, Block):
			self.namespace = block.namespace
			self.name = block.name
			self.blockState = block.blockState.copy()
			return
		parts = block.split(':')
		self.blockState = dict()
		if '=' in parts[-1]:
			states = parts.pop()
			for state_str in states.split(','):
				key, val = state_str.split('=')
				self.blockState[key] = val
		self.name = parts.pop()
		self.namespace = parts[0] if parts else "minecraft"

	def isParentOf(self, other:Block):
		return (
			self.namespace == other.namespace and 
			self.name == other.name and 
			other.blockState.items() <= self.blockState.items()
		)
	
	def __eq__(self, other:Block):
		if not isinstance(other, Block):
			return False
		return (
			self.namespace == other.namespace and
			self.name == other.name and
			self.blockState == other.blockState
		)

	def __le__(self, other):
		if not isinstance(other, Block):
			raise ValueError("Cannot compare a Block to a {}".format(type(other)))
		return self.isParentOf(other)
	
	def __ge__(self, other):
		return other <= self

# def namespace(block:str):
# 	parts = block.split(':')
# 	if '=' in parts[-1]:
# 		parts.pop()
# 	if len(parts) == 1:
# 		return 'minecraft'
# 	return parts[0]

# def with_namespace(block:str):
# 	parts = block.split(':')
# 	if len(parts) < (3 if '=' in parts[-1] else 2):
# 		return 'minecraft:{}'.format(block)
# 	return block

# def base(block:str):
# 	parts = block.split(':')
# 	if '=' in parts[-1]:
# 		parts.pop()
# 	if len(parts) < 2:
# 		parts.insert(0, 'minecraft')
# 	return ':'.join(parts)

# def encapsulates(block, filter):
# 	if '=' in block:
# 		return block == filter
# 	return block == base(filter)

# def encapsulated_by(block, filter):
# 	if block == filter:
# 		return True
# 	if '=' not in filter:
# 		return base(block) == filter
# 	return False

# def in_(block:str, row:List[str], fn=encapsulated_by):
# 	"""Returns true if the given block is encapsulated by any block in this row"""
# 	for existing in row:
# 		if fn(block, existing):
# 			return True
# 	return False
	
		