import csv
from pathlib import Path
from typing import List
from . import files
from . import blocks as Blocks

def get_blocks(tag:str|Path):
	if isinstance(tag, Path):
		path = tag
		tag = files.get_tag(tag)
	else:
		path = files.get_path(tag)
	if not files.is_tag(tag):
		raise ValueError('No such tag:', tag)
	val_index = -1
	if ':' in tag:
		tag, val = tag.split(':')
		if not files.is_enum(tag):
			raise ValueError('Tag {} is not an enum'.format(tag[:tag.index(':')]))
		vals = values(tag)
		val_index = vals.index(val)
		if val_index == -1:
			raise ValueError('Enum {} has no value {}'.format(tag, val))
	out = []
	with path.joinpath(files.BLOCKS_FILE).open() as stream:
		for i, row in enumerate(csv.reader(stream, delimiter='\t')):
			if i == val_index or val_index == -1:
				out.extend(row)
	return out


def has_tag(block:str, tag:str):
	"""Determine if a single block has a tag"""
	if not files.is_tag(tag):
		raise ValueError('No such tag:', tag)
	with open(files.get_blocks_file(tag), 'r') as blocks_f:
		for row in csv.reader(blocks_f, delimiter='\t'):
			if Blocks.in_(block, row):
				return True
	return False

def have_tag(blocks:List[str], tag:str):
	"""Determine if a collection of blocks all have a tag"""
	return not missing_from(blocks, tag)

def remainder(a:List[str], b:List[str]):
	"""Return the blocks that are in a but not in b"""
	return [block for block in a if not Blocks.in_(block, b)]

def missing_from(blocks:List[str], tag:str):
	if not files.is_tag(tag):
		raise ValueError('No such tag: {}'.format(tag))
	
	missing = blocks.copy()
	with open(files.get_blocks_file(tag), 'r') as blocks_f:
		for row in csv.reader(blocks_f, delimiter='\t'):
			missing = remainder(missing, row)
		if not missing:
			return []
	return missing

def values(tag:str):
	"""Get the possible values of an enum tag"""
	if not files.is_enum(tag):
		raise ValueError('No such enum: {}'.format(tag))
	with open(files.get_structure_file(tag), 'r') as fr:
		return [str.strip() for str in fr.read().split('\t')]