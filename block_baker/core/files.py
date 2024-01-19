from pathlib import Path

BLOCKS_FILE = '__blocks.tsv'
STRUCTURE_FILE = '__structure.tsv'
DATA_DIR = Path('./data')

def get_path(tag:str):
	if ':' in tag:
		tag = tag[:tag.index(':')]
	return DATA_DIR.joinpath(*(tag.split('/')))

def get_tag(path:Path):
	return str(path.relative_to(DATA_DIR))

def get_blocks_file(tag:str):
	if ':' in tag:
		tag = tag[:tag.index(':')]
	return DATA_DIR.joinpath(*(tag.split('/')), BLOCKS_FILE)

def get_structure_file(tag:str):
	if ':' in tag:
		tag = tag[:tag.index(':')]
	return DATA_DIR.joinpath(*(tag.split('/')), STRUCTURE_FILE)

def get_parents(tag:str):
	components = tag.split('/')
	if len(components) > 1:
		return ['/'.join(components[:i]) for i in range(1, len(components))]
	return []

def get_children(tag:str):
	path = get_path(tag)
	out = []
	for child_path in path.rglob('./[a-zA-Z0-9]*'):
		out.append(str(child_path.relative_to(DATA_DIR)))
	return out

def is_tag(tag:str):
	return get_blocks_file(tag).is_file()

def is_bool(tag:str):
	return get_blocks_file(tag).is_file() and not get_structure_file(tag).is_file()

def is_enum(tag:str):
	return get_blocks_file(tag).is_file() and get_structure_file(tag).is_file()