import unittest

from core.block import Block, BlockCollection

class TestBlock(unittest.TestCase):
	def test_parent(self):
		self.assertTrue(Block.from_str('oak_stairs') >= Block.from_str('minecraft:oak_stairs'))
		self.assertTrue(Block.from_str('oak_stairs:half=bottom') >= Block.from_str('oak_stairs:half=bottom:facing=north'))
		self.assertTrue(Block.from_str('oak_stairs:half=bottom:facing=north,east').isParentOf(Block.from_str('oak_stairs:half=bottom:facing=north')))
		self.assertFalse(Block.from_str('oak_stairs:half=bottom:facing=north').isParentOf(Block.from_str('oak_stairs:half=bottom:facing=north,east')))
	
	def test_child(self):
		self.assertTrue(Block.from_str('oak_stairs').isChildOf(Block.from_str('minecraft:oak_stairs')))
		self.assertTrue(Block.from_str('oak_stairs:half=bottom:facing=north') <= Block.from_str('oak_stairs:half=bottom'))
		self.assertTrue(Block.from_str('oak_stairs:half=bottom:facing=north').isChildOf(Block.from_str('oak_stairs:half=bottom:facing=north,east')))
		self.assertFalse(Block.from_str('oak_stairs:half=bottom:facing=north,east').isChildOf(Block.from_str('oak_stairs:half=bottom:facing=north')))
	
	def test_with_state(self):
		self.assertEqual(Block.from_str('oak_stairs').with_state({'half':['bottom']}), Block.from_str('oak_stairs:half=bottom'))
		self.assertEqual(Block.from_str('oak_stairs:facing=north').with_state({'half':['bottom']}), Block.from_str('oak_stairs:facing=north:half=bottom'))
		self.assertEqual(Block.from_str('oak_stairs:facing=north,east').with_state({'facing':['east']}), Block.from_str('oak_stairs:facing=east'))
		self.assertIsNone(Block.from_str('oak_stairs:half=top').with_state({'half':['bottom']}))
	
class TestBlockCollection(unittest.TestCase):
	def test_add(self):
		bc = BlockCollection.from_strings
		self.assertEqual(bc(['oak_stairs']).insert(bc(['birch_stairs'])), bc(['oak_stairs', 'birch_stairs']))
		self.assertEqual(bc(['oak_stairs', 'birch_stairs']).insert(bc(['birch_stairs'])), bc(['oak_stairs', 'birch_stairs']))
		self.assertEqual(bc(['oak_stairs:half=bottom']).insert(bc(['oak_stairs:half=top'])), bc(['oak_stairs:half=bottom', 'oak_stairs:half=top']))
	
	def test_remove(self):
		bc = BlockCollection.from_strings
		self.assertEqual(bc(['oak_stairs']).remove(bc(['birch_stairs'])), bc(['oak_stairs']))
		self.assertEqual(bc(['oak_stairs', 'birch_stairs']).remove(bc(['birch_stairs'])), bc(['oak_stairs']))
		self.assertEqual(bc(['oak_stairs:half=bottom']).remove(bc(['oak_stairs:half=top'])), bc(['oak_stairs:half=bottom']))
		self.assertEqual(bc(['oak_stairs:half=bottom,top']).remove(bc(['oak_stairs:half=top'])), bc(['oak_stairs:half=bottom']))
		self.assertEqual(bc(['oak_stairs:facing=north:half=top,bottom']).remove(bc(['oak_stairs:facing=north:half=bottom'])), bc(['oak_stairs:facing=north:half=top']))