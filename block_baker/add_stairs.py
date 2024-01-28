import library

def main():
	library.bool_tag('create', 'stairs/topSolid')
	library.bool_tag('create', 'stairs/bottomSolid')
	library.bool_tag('create', 'stairs/northSolid')
	library.bool_tag('create', 'stairs/southSolid')
	library.bool_tag('create', 'stairs/eastSolid')
	library.bool_tag('create', 'stairs/westSolid')

	stair_types = ["minecraft:purpur_stairs", "minecraft:brick_stairs", "minecraft:nether_brick_stairs", "minecraft:red_nether_brick_stairs", "minecraft:quartz_stairs", "minecraft:smooth_quartz_stairs", "minecraft:oak_stairs", "minecraft:spruce_stairs", "minecraft:birch_stairs", "minecraft:jungle_stairs", "minecraft:acacia_stairs", "minecraft:dark_oak_stairs", "minecraft:prismarine_stairs", "minecraft:prismarine_brick_stairs", "minecraft:dark_prismarine_stairs", "minecraft:stone_stairs", "minecraft:cobblestone_stairs", "minecraft:mossy_cobblestone_stairs", "minecraft:stone_brick_stairs", "minecraft:mossy_stone_brick_stairs", "minecraft:blackstone_stairs", "minecraft:polished_blackstone_stairs", "polished_blackstone_brick_stairs", "minecraft:sandstone_stairs", "minecraft:smooth_sandstone_stairs", "minecraft:red_sandstone_stairs", "minecraft:smooth_red_sandstone_stairs", "minecraft:crimson_stairs", "minecraft:warped_stairs", "minecraft:polished_granite_stairs", "minecraft:polished_diorite_stairs", "minecraft:polished_andesite_stairs", "minecraft:granite_stairs", "minecraft:diorite_stairs", "minecraft:andesite_stairs", "minecraft:end_stone_brick_stairs"]
	states = [
		("shape=outer_left,half=bottom",  ["stairs/bottomSolid"]),
		("shape=outer_left,half=top",     ["stairs/topSolid"]),

		("shape=outer_right,half=bottom", ["stairs/bottomSolid"]),
		("shape=outer_right,half=top",    ["stairs/topSolid"]),
	]
	directions = ["north", "east", "south", "west"]
	triplets = [(directions[i-1], directions[i], directions[(i+1) % len(directions)]) for i in range(len(directions))]
	for l, s, r in triplets:
		states.extend([
			("shape=straight,half=bottom,facing={}".format(s), ["stairs/{}Solid".format(s), "stairs/bottomSolid"]),
			("shape=straight,half=top,facing={}".format(s), ["stairs/{}Solid".format(s), "stairs/topSolid"]),

			("shape=inner_left,half=bottom,facing={}".format(s), ["stairs/{}Solid".format(s), "stairs/{}Solid".format(l), "stairs/bottomSolid"]),
			("shape=inner_left,half=top,facing={}".format(s), ["stairs/{}Solid".format(s), "stairs/{}Solid".format(l), "stairs/topSolid"]),

			("shape=inner_right,half=bottom,facing={}".format(s), ["stairs/{}Solid".format(s), "stairs/{}Solid".format(r), "stairs/bottomSolid"]),
			("shape=inner_right,half=top,facing={}".format(s), ["stairs/{}Solid".format(s), "stairs/{}Solid".format(r), "stairs/topSolid"])
		])
	for (state, tags) in states:
		blocks = ["{}:{}".format(block, state) for block in stair_types]
		library.edit_blocks(blocks, tags, [])
	print("Done!")

if __name__ == "__main__":
	main()