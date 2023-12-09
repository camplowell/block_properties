from typing import List
from core import files, query
from core import blocks as Blocks

def _get_lines(tag:str):
	count = 0
	with files.get_blocks_file(tag).open() as f:
		for count_, _ in enumerate(f.readlines()):
			count = count_ + 1
	return count

def _matches_permissive(current:str, parent:str):
	if '=' in current and '=' in parent:
		return parent == current
	if '=' in parent:
		return parent == Blocks.base(current)
	return Blocks.base(parent) == current
def _missing(current:List[str], parent:List[str]):
	current = current.copy()
	for block_p in parent:
		current = [block_c for block_c in current if not _matches_permissive(block_c, block_p)]
	current

def _verify_r(tag:str, parent_blocks:List[str]):
	bad = False
	current_blocks = query.get_blocks(tag)
	if parent_blocks is not None:
		missing = _missing(current_blocks, parent_blocks)
		if missing:
			print('The tags {} are prerent in the tag {} but not in its parent.'.format(missing, tag))
			bad = True
	if files.is_enum(tag):
		expected_rows = len(query.values(tag))
	else:
		expected_rows = 1
	actual_rows = _get_lines(tag)
	if actual_rows > expected_rows:
		print('There are too many rows in {} (expected {}; got {})'.format(tag, expected_rows, actual_rows))
	for child in files.get_children(tag):
		bad |= _verify_r(child, current_blocks)
	return bad

def main():
	bad = False
	for path_object in files.DATA_DIR.glob('./[a-zA-Z0-9]*'):
		bad |= _verify_r(files.get_tag(path_object), None)
	if not bad:
		print('No errors found!')

if __name__ == "__main__":
	main()