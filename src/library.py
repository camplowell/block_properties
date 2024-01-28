import argparse
from enum import Enum
from typing import List
import shutil

from core.block import Block, BlockCollection
from argparse_formatter import Formatter
from core.tag import BoolTag, EnumTag, Tag, TagLibrary
from evaluation.evaluator import evaluate
from mixins.register import register_all_mixins

DATA_DIR = './data'
library = TagLibrary(DATA_DIR)
register_all_mixins(library)

class TagType(Enum):
	boolean = 'boolean'
	enum = 'enum'

def create_tag(tag:str, values:List[str] = []):
	if values:
		tag_ = library.create_enum(tag, values)
	else:
		tag_ = library.create_bool(tag)
	tag_.save()

def edit_tag(tag:str, add:List[str], remove:List[str], force:bool):
	tag_ = library.get(tag)
	if not isinstance(tag_, EnumTag):
		print('Cannot edit non-enum tags!')
	
	ignore = [value for value in remove if value in add]
	if ignore:
		print('The vaules {ignore} were in both add and remove; ignoring.')
		add = [value for value in add if value not in ignore]
		remove = [value for value in remove if value not in ignore]

	for value in add:
		tag_.add_value(value)
	for value in remove:
		tag_.remove_value(value)
	tag_.save()

def delete_tag(tag:str, force:bool):
	if not force and library.get(tag).get():
		confirm = input(f'You are about to delete the tag {tag}. Continue? (y/n)')
		if confirm.lower() != 'y':
			print('Canceled.')
			exit()
	library.delete(tag)
	print('Removed!')

def tag_blocks(blocks:List[str], add:List[str], remove:List[str]):
	collection = BlockCollection.from_strings(blocks)
	ignore = [tag for tag in remove if tag in add]
	if ignore:
		print('The tags {ignore} were in both add and remove; ignoring.')
		add = [tag for tag in add if tag not in ignore]
		remove = [tag for tag in remove if tag not in ignore]
	# Ensure all tags exist before proceeding
	to_save:List[BoolTag|EnumTag] = []
	for tag in add:
		value = None
		if ':' in tag:
			tag, value = tag.split(':')
		tag_ = library.get(tag)
		if isinstance(tag_, EnumTag):
			tag_.add(value, collection)
		elif isinstance(tag_, BoolTag):
			if value:
				print(f'Cannot specify value for boolean tag {tag}')
				exit()
			tag_.add(collection)
		else:
			print(f'Tag {tag} if of unsupported type {type(tag_)}')
			exit()
		to_save.append(tag_)
	
	for tag in remove:
		value = None
		if ':' in tag:
			tag, value = tag.split(':')
		tag_ = library.get(tag)
		if isinstance(tag_, EnumTag):
			tag_.remove(value, collection)
		elif isinstance(tag_, BoolTag):
			if value:
				print(f'Cannot specify value for boolean tag {tag}')
				exit()
			tag_.remove(collection)
		else:
			print(f'Tag {tag} if of unsupported type {type(tag_)}')
			exit()
		to_save.append(tag_)
	
	for tag in to_save:
		tag.save()

def query(expression:str):
	if isinstance(expression, list):
		expression = ' '.join(expression)
	print(f'Evaluating expression {expression}')
	print(repr(evaluate(expression, library)))

arg_parser = argparse.ArgumentParser(
	prog="library",
	description="Edit the tags of blocks",
	epilog='Nested tags are written as "parent/child" and enum tags are written as "tag:value"',
	formatter_class=Formatter
)

subparsers = arg_parser.add_subparsers()

tag_parser = subparsers.add_parser('tag', help='Manipulate tags', formatter_class=Formatter)
tag_subparsers = tag_parser.add_subparsers()

create_parser = tag_subparsers.add_parser('create', help='Create tags', formatter_class=Formatter)
create_parser.add_argument('tag', type=str)
create_parser.add_argument('-v', '--values', type=str, nargs='+', help='Make an enumerated tag with named values', default=[])
create_parser.set_defaults(func=create_tag)

edit_parser = tag_subparsers.add_parser('edit', help='Edit the values of enumerated tags', formatter_class=Formatter)
edit_parser.add_argument('tag', type=str)
edit_parser.add_argument('-a', '--add', type=str, nargs='+', help='Add values', default=[])
edit_parser.add_argument('-r', '--remove', type=str, nargs='+', help='Remove values', default=[])
edit_parser.add_argument('-f', '--force', help='Delete the tag without confirming', action='store_true')
edit_parser.set_defaults(func=edit_tag)

delete_parser = tag_subparsers.add_parser('delete', help='Delete tags', formatter_class=Formatter)
delete_parser.add_argument('tag', type=str)
delete_parser.add_argument('-f', '--force', help='Delete the tag without confirming', action='store_true')
delete_parser.set_defaults(func=delete_tag)

block_parser = subparsers.add_parser('blocks', help='Manipulate blocks', formatter_class=Formatter)
block_parser.add_argument('blocks', type=str, nargs='*', help='The blocks to manipulate', metavar='BLOCKS')
action_grp = block_parser.add_argument_group('actions')
action_grp.add_argument('-a', '--add', type=str, nargs='*', help='Tags to add', required=False, metavar='TAGS', default=[])
action_grp.add_argument('-r', '--remove', type=str, nargs='*', help='Tags to remove', required=False, metavar='TAGS', default=[])
block_parser.set_defaults(func=tag_blocks)

query_parser = subparsers.add_parser('query', help='Query the library', formatter_class=Formatter)
query_parser.add_argument('expression', type=str, nargs='+')
query_parser.set_defaults(func=query)

if __name__ == "__main__":
	args = arg_parser.parse_args()
	func = args.func
	delattr(args, 'func')
	func(**args.__dict__)