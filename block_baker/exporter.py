import argparse
from pathlib import Path
import json
from typing import Dict, List
from evaluation.evaluator import evaluate
import sys

arg_parser = argparse.ArgumentParser(
	prog="exporter",
	description="Assemble tags into block.properties files",
	epilog='Nested tags are written as "parent/child" and enum tags are written as "tag:value"'
)

def swizzle(a:set, b:set):
	return (a.difference(b), b.difference(a), a.intersection(b))

def bakeState(states) -> Dict[frozenset, set]:
	all_states = dict()
	for state, expression in states.items():
		current_blocks = set(evaluate(expression))
		existing_keys = list(all_states.keys())
		for key in existing_keys:
			all_states[key], current_blocks, all_states[key.union([state])] = swizzle(all_states[key], current_blocks)
		all_states[frozenset([state])] = current_blocks
	
	return {k:v for (k,v) in all_states.items() if len(v)}

def generate_properties_file(path:Path, ids:Dict[frozenset, set]):
	lines = []
	for i, (mask, blocks) in enumerate(ids.items()):
		lines.append("\n# {}".format(', '.join(mask)))
		lines.append("block.{} = {}".format(i + 1, ' '.join(blocks)))
	with path.open('w') as writer:
		writer.write('\n'.join(lines))

def generate_decoder_file(path:Path, masks:List[frozenset], states:List[str]):
	lines = [
		"#if !defined(BLOCK_PROPERTIES_DECODER)",
		"#define BLOCK_PROPERTIES_DECODER"
	]
	for state in states:
		valid_ids = ["id == {}".format(i + 1) for i, mask in enumerate(masks) if state in mask]
		lines.append("\nbool {}(int id) {{".format(state))
		lines.append("    return {};".format(' || '.join(valid_ids) if valid_ids else 'false'))
		lines.append("}")
	
	lines.append("\n#endif // EOF")
	with path.open('w') as writer:
		writer.write('\n'.join(lines))

def export(config:str):
	config_path = Path(config)
	with config_path.open() as config_source:
		config_json = json.load(config_source)
	config_dir = config_path.parent.relative_to('.')
	
	props_path = config_dir.joinpath(config_json['properties_file'])
	decoder_path = config_dir.joinpath(config_json['decoder_file'])
	print('Properties: {}'.format(props_path))
	print('Decoder: {}'.format(decoder_path))

	states = list(dict(config_json['states']).keys())
	ids = bakeState(dict(config_json['states']))
	generate_properties_file(props_path, ids)
	generate_decoder_file(decoder_path, list(ids.keys()), states)
	


arg_parser.add_argument('config', type=str)

if __name__ == "__main__":
	if sys.version_info < (3, 7):
		sys.exit("Python 3.7 or later is required.")
	args = arg_parser.parse_args()
	export(**args.__dict__)