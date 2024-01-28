import argparse
import json
from pathlib import Path
from typing import Dict, FrozenSet, Iterable

from core.block import BlockCollection
from core.tag import TagLibrary
from evaluation.evaluator import evaluate
from mixins.register import register_all_mixins

DATA_DIR = './data'
library = TagLibrary(DATA_DIR)
register_all_mixins(library)
LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

def swizzle(a:BlockCollection, b:BlockCollection):
	both = a.intersection(b)
	return (a - b, b - a, both)

def bake_masks(states:Dict[str, str]):
	result:Dict[FrozenSet[str], BlockCollection] = dict()
	print('Evaluating flags...')
	queue = [(frozenset([key]), evaluate(expr, library)) for (key, expr) in states.items()]
	num_keys = len(queue)
	i = 1
	print('Baking masks...')
	while queue:
		key, blocks = queue.pop()
		if len(key) == 1:
			if i > 1:
				print(LINE_UP, end=LINE_CLEAR)
			print(f'    {list(key)[0]} ({i}/{num_keys})')
			i += 1
		for key_v in list(result.keys()):
			both_key = key_v.union(key)
			if both_key == key or both_key == key_v:
				continue
			result[key_v], blocks, both = swizzle(result[key_v], blocks)
			if both:
				queue.append((key_v.union(key), both))
		if blocks:
			result[key] = blocks
	print(LINE_UP, end=LINE_CLEAR)
	return {k:v for (k,v) in result.items() if len(v)}

def generate_properties_file(path:Path, masks:Dict[FrozenSet[str], BlockCollection]):
	lines = []
	for i, (mask, blocks) in enumerate(masks.items()):
		lines.append(f'\n# {", ".join(mask)}')
		lines.append(f'block.{i + 1} = {repr(blocks)}')
	
	with path.open('w') as writer:
		writer.write('\n'.join(lines))

def generate_decoder_file(path:Path, masks:Dict[FrozenSet[str], BlockCollection], states:Iterable[str]):
	lines = [
		"#if !defined(BLOCK_PROPERTIES_DECODER)",
		"#define BLOCK_PROPERTIES_DECODER"
	]

	for state in states:
		valid_ids = ["id == {}".format(i + 1) for (i, mask) in enumerate(masks) if state in mask]
		lines.append(f'\nbool {state}(int id) {{')
		lines.append(f'    return {" || ".join(valid_ids) if valid_ids else "false"};')
		lines.append( "}")

	lines.append("\n#endif // EOF")
	
	with path.open('w') as writer:
		writer.write('\n'.join(lines))
	
def export(config:str):
	config_path = Path(config)
	with config_path.open() as config_stream:
		config_json = json.load(config_stream)
	print(f'Loaded configuration at {config_path}.')
	config_dir = config_path.parent

	props_path = config_dir.joinpath(config_json['properties_file'])
	decoder_path = config_dir.joinpath(config_json['decoder_file'])
	
	flags = dict(config_json['flags'])
	states = list(flags.keys())
	print(f'Found {len(states)} flags.')
	masks = bake_masks(flags)
	print(f'Outputting to disk...')
	generate_properties_file(props_path, masks)
	generate_decoder_file(decoder_path, masks, states)
	print('Done!')

arg_parser = argparse.ArgumentParser(
	prog="exporter",
	description="Assemble tags into block.properties files",
	epilog='Nested tags are written as "parent/child" and enum tags are written as "tag:value"'
)

arg_parser.add_argument('config', type=str)

if __name__ == "__main__":
	args = arg_parser.parse_args()
	export(**args.__dict__)