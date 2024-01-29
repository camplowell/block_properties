## Backends
### tags
Manage a collection of block tags on disk and in memory
- [x] Named tags
- [x] Nested tags
- [x] Enumerated tags
- [x] Memory-only library
- [x] Derived tags
### exporter.py
Generate the `block.properties` and `block_ids.glsl` files
- [x] Tag filters
- [x] Input from JSON string
- [x] Assign unique IDs to filter combos
- [x] Generate `block_ids.glsl`
- [ ] Support special cases
	- [ ] Ensure `block_ids.glsl` still decodes special case features
- [ ] Conditional inclusion (`#ifdef`) support
### Combinations
- [x] Basic list manipulations (union, difference, intersection)
- [x] Support blockstate with single values
- [x] Support blockstate with multiple values

## Frontends
### library.py
A CLI editor for the library.
- [x] Add/remove tags to/from blocks
- [x] Create new enum or boolean tags
- [x] Delete tags
- [x] Edit the options of enum tags
- [x] Nested tags
### exporter.py
A command-line interface for the generator.
- [x] Loads a config file path
- [x] Saves the generated files in sensible (or specified) locations
### Web interface
A visual interface for exporter.py
- [ ] Run a pre-defined JSON (using pyscript?)
- [ ] Visual config editor
	- [ ] Toggle features
	- [ ] Enum features
	- [ ] Nested features (separate from enum)
	- [ ] Conditional inclusion
- [ ] Run `generator_core.py` in the browser
- [ ] Save the output files