import re
from typing import List

def namespace(block:str):
	parts = block.split(':')
	if '=' in parts[-1]:
		parts.pop()
	if len(parts) == 1:
		return 'minecraft'
	return parts[0]

def with_namespace(block:str):
	parts = block.split(':')
	if len(parts) < (3 if '=' in parts[-1] else 2):
		return 'minecraft:{}'.format(block)
	return block

def base(block:str):
	parts = block.split(':')
	if '=' in parts[-1]:
		parts.pop()
	if len(parts) < 2:
		parts.insert(0, 'minecraft')
	return ':'.join(parts)

def encapsulates(block, filter):
	if '=' in block:
		return block == filter
	return block == base(filter)

def encapsulated_by(block, filter):
	if block == filter:
		return True
	if '=' not in filter:
		return base(block) == filter
	return False

def in_(block:str, row:List[str], fn=encapsulated_by):
	"""Returns true if the given block is encapsulated by any block in this row"""
	for existing in row:
		if fn(block, existing):
			return True
	return False
	
		