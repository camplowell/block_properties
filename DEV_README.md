## Backends
### library.py
A CLI editor for the library.
- [x] Add/remove tags to/from blocks
- [x] Create new enum or boolean tags
- [x] Delete tags
- [x] Edit the options of enum tags
- [x] Nested tags
### exporter.py
Generate the `block.properties` and `block_ids.glsl` files
- [x] Tag filters
- [x] Input from JSON string
- [x] Assign unique IDs to filter combos
- [x] Generate `block_ids.glsl`
- [ ] Support special cases
	- [ ] Ensure `block_ids.glsl` still decodes special case features
- [ ] Conditional inclusion (`#ifdef`) support
### validator.py
Checks the integrity of the library.
- [ ] Detect folders without `__blocks.tsv` files
- [x] Detect `__blocks.tsv` files with the wrong number of rows
- [x] Detect nested attributes that aren't in their parent

## Frontends
### exporter.py
A command-line interface for the generator.
- [x] Loads a config file path
- [x] Saves the generated files in sensible (or specified) locations
### index.html
Runs generator_core.py using pyscript (a WebAssembly Python interpreter)
- [ ] Visual config editor
	- [ ] Toggle features
	- [ ] Enum features
	- [ ] Nested features (separate from enum)
	- [ ] Conditional inclusion
- [ ] Run `generator_core.py` in the browser
- [ ] Save the output files