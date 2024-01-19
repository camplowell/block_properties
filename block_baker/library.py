import argparse
import csv
from enum import Enum
import os
from os import path
import shutil
from typing import List
from pathlib import Path

from core import files, query
from core import blocks as Blocks
from core.files import get_path, get_blocks_file, get_structure_file, is_tag, is_enum, is_bool, get_parents

parser = argparse.ArgumentParser(
	prog="compendium",
	description="An editor for the block features compendium",
	epilog='Nested tags are written as "parent/child" and enum tags are written as "tag:value"'
)

class BoolAction(Enum):
	create = 'create'
	delete = 'delete'

class EnumAction(Enum):
	create = 'create'
	delete = 'delete'
	add = 'add'
	remove = 'remove'

def _remove(target_path:Path):
	confirm = input('You are about to delete the tag {}. Continue? (y/n)\n'.format(files.get_tag(target_path)))
	if confirm.lower() == 'y':
		shutil.rmtree(target_path)
		print('Removed!')
	else:
		print('Canceled.')

def bool_tag(action:BoolAction, target:str):
	target_path = files.get_path(target)
	if action == BoolAction.delete:
		if not is_bool(target):
			print('No such boolean tag: {}'.format(target))
			exit()
		_remove(target_path)
		return
	if is_tag(target):
		print('Tag already exists: {}'.format(target))
		exit()
	os.makedirs(target_path)
	with get_blocks_file(target).open('a'):
		pass
	print('Created boolean tag: {}'.format(target))
		
def enum_create(target:str, values:List[str]):
	target_path = get_path(target)
	if is_tag(target):
		print('Tag already exists: {}'.format(target))
		exit()
	os.makedirs(target_path)
	with get_blocks_file(target).open('a') as blocks_w:
		if values:
			blocks_w.write('\n' * (len(values) - 1))
	with get_structure_file(target).open('a') as structure:
		if values:
			values.sort(key=Blocks.namespace)
			csv_w = csv.writer(structure, delimiter='\t')
			csv_w.writerow(values)
	print('Created enum tag: {}'.format(target))
	
def enum_delete(target:str):
	target_path = get_path(target)
	if not is_enum(target):
		print('No such enum: {}'.format(target))
		exit()
	_remove(target_path)
	
def merge(old:List[str], add:List[str]):
	i_old = 0
	i_add = 0
	structure = []
	while i_old < len(old) and i_add < len(add):
		if old[i_old] < add[i_add]:
			structure.append(old[i_old])
			i_old += 1
		elif add[i_add] < old[i_old]:
			structure.append(add[i_add])
			i_add += 1
		else:
			i_old += 1
	return structure + add[i_add:] + old[i_old:]

def enum_edit(target:str, add:List[str], remove:List[str]):
	structure_path = get_structure_file(target)
	blocks_path = get_blocks_file(target)
	if not is_enum(target):
		print('No such enum: {}'.join(target))
	
	add.sort()
	old = query.values(target)

	structure = [val for val in merge(old, add) if val not in remove]
	with structure_path.open('w') as structure_fw:
		csv_w = csv.writer(structure_fw, delimiter='\t')
		csv_w.writerow(structure)
	
	with blocks_path.open('r') as blocks_fr:
		lines = [line.strip() for line in blocks_fr.readlines()]
	
	newlines = []
	for item in structure:
		if item in lines:
			i_old = lines.index(item)
			newlines.append(lines[i_old])
		else:
			newlines.append('')
	with blocks_path.open('w') as blocks_fw:
		blocks_fw.write('\n'.join(newlines))
	print('Edited enum {}'.format(target))

def _add_blocks(tag:str, add:List[str], * , value:str=...):
	i = 0
	if not is_tag(tag):
		print('No such tag: {}'.format(tag))
	if value is not ...:
		structure = query.values(tag)
		if value not in structure:
			print('Enum {} has no value "{}"'.format(tag, value))
			exit()
		i = structure.index(value)
	blocks_path = get_blocks_file(tag)
	with blocks_path.open('r') as blocks_r:
		data = [line for line in csv.reader(blocks_r, delimiter='\t')]
	while len(data) <= i:
		data.append([])
	add = [block for block in add if not Blocks.in_(block, data[i])] # Don't add if a more general version is already present 
	data[i] = (
		[block for block in data[i] if not Blocks.in_(block, add)] + # Toss specific states if a more general version is being added
		add
	)
	data[i].sort(key=Blocks.namespace) # Ensure namespaces stick together
	with blocks_path.open('w') as blocks_w:
		writer = csv.writer(blocks_w, delimiter='\t')
		writer.writerows(data)
	print('Added {} blocks to {}'.format(len(add), tag))

def _remove_blocks(tag:str, remove:List[str], * , value:str=...):
	i_filter = -1
	if value is not ...:
		structure = query.values(tag)
		if value not in structure:
			print('Enum {} has no value "{}"'.format(tag, value))
			exit()
		i_filter = structure.index(value)
	blocks_path = files.get_blocks_file(tag)
	data = []
	num_removed = 0
	with blocks_path.open('r') as blocks_r:
		for i, row in enumerate(csv.reader(blocks_r, delimiter='\t')):
			if i_filter >= 0 and i != i_filter:
				data.append(row)
			else:
				data.append([block for block in row if not Blocks.in_(block, remove)])
				num_removed += len(row) - len(data[-1])
	
	with blocks_path.open('w') as blocks_w:
		csv_w = csv.writer(blocks_w)
		csv_w.writerows(data)
	if num_removed:
		print('Removed {} blocks from {}'.format(num_removed, tag))

def _add_parents(tags, add):
	missing_queue = []
	for tag in tags:
		for parent in get_parents(tag):
			missing = query.missing_from(add, parent)
			if missing and is_enum(parent):
				print('Cannot automatically add blocks to enum parent {}.'.format(parent))
				print('Missing blocks:')
				print(missing)
				exit()
			elif missing:
				missing_queue.append((parent, missing))
	for tag, missing in missing_queue:
		_add_blocks(tag, missing)

def _remove_children(tag:str, blocks:List[str]):
	for child in files.get_children(tag):
		_remove_blocks(child, blocks)

def edit_blocks(blocks:List[str], add:List[str], remove:List[str]):
	blocks = [Blocks.with_namespace(block) for block in blocks]
	if add:
		_add_parents(add, blocks)
		for tag in add:
			if ':' in tag:
				tag, value = tag.split(':')
				_add_blocks(tag, blocks, value=value)
			else:
				_add_blocks(tag, blocks)
	for tag in remove:
		_remove_children(tag, blocks)
		if ':' in tag:
			tag, value = tag.split(':')
			_remove_blocks(tag, blocks, value=value)
		else:
			_remove_blocks(tag, blocks)

def query_blocks(tag:str):
	print(' '.join(query.get_blocks(tag)))

subparsers = parser.add_subparsers() 

flag_parser = subparsers.add_parser('bool', help="Create or delete boolean tags")
flag_parser.add_argument('action', type=BoolAction, help='{create, delete}')
flag_parser.add_argument('target', type=str, help='The tag')
flag_parser.set_defaults(func=bool_tag)

option_parser = subparsers.add_parser('enum', help="Create, delete, or edit enumerated tags")
option_subparsers = option_parser.add_subparsers()

create_option_parser = option_subparsers.add_parser('create')
create_option_parser.add_argument('target', type=str, help='The tag')
create_option_parser.add_argument('--values', '-v', type=str, nargs='+', help='The values of the enumerated tag')
create_option_parser.set_defaults(func=enum_create)

delete_option_parser = option_subparsers.add_parser('delete')
delete_option_parser.add_argument('target', type=str, help='The tag')
delete_option_parser.set_defaults(func=enum_delete)

edit_option_parser = option_subparsers.add_parser('edit')
edit_option_parser.add_argument('target', type=str, help='The tag')
edit_option_parser.add_argument('--add', '-a', type=str, nargs='+', default=[])
edit_option_parser.add_argument('--remove', '-r', type=str, nargs='+', default=[])
edit_option_parser.set_defaults(func=enum_edit)

blocks_parser = subparsers.add_parser('blocks', help="Add tags to blocks")
blocks_parser.add_argument('blocks', type=str, nargs='+')
blocks_parser.add_argument('--add', '-a', type=str, nargs='+', default=[], help='Add these tags.')
blocks_parser.add_argument('--remove', '-r', type=str, nargs='+', default=[], help='Remove these tags.')
blocks_parser.set_defaults(func=edit_blocks)

query_parser = subparsers.add_parser('query', help="Query the library")
query_parser.add_argument('tag', type=str)
query_parser.set_defaults(func=query_blocks)

if __name__ == "__main__":
	args = parser.parse_args()
	func = args.func
	delattr(args, 'func')
	func(**args.__dict__)