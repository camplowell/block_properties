import unittest

from core.block import Block, BlockCollection

class TestBlock(unittest.TestCase):
	def test_parent(self):
		self.assertTrue(Block.from_str('oak_stairs') >= Block.from_str('minecraft:oak_stairs'))
		self.assertTrue(Block.from_str('oak_stairs:half=bottom') >= Block.from_str('oak_stairs:half=bottom:facing=north'))
		self.assertFalse(Block.from_str('oak_stairs:half=bottom:facing=north').isParentOf(Block.from_str('oak_stairs:half=bottom')))
		self.assertTrue(Block.from_str('oak_stairs:half=top').isParentOf(Block.from_str('oak_stairs:half=top')))
		self.assertFalse(Block.from_str('oak_stairs:half=top').isParentOf(Block.from_str('oak_stairs:half=bottom')))
	
	def test_child(self):
		self.assertTrue(Block.from_str('oak_stairs').isChildOf(Block.from_str('minecraft:oak_stairs')))
		self.assertTrue(Block.from_str('oak_stairs:half=bottom:facing=north').isChildOf(Block.from_str('oak_stairs:half=bottom')))
		self.assertFalse(Block.from_str('oak_stairs:half=bottom').isChildOf(Block.from_str('oak_stairs:half=bottom:facing=north')))
	
	def test_with_state(self):
		self.assertEqual(Block.from_str('oak_stairs').with_state({'half':'bottom'}), Block.from_str('oak_stairs:half=bottom'))
		self.assertEqual(Block.from_str('oak_stairs:facing=north').with_state({'half':'bottom'}), Block.from_str('oak_stairs:facing=north:half=bottom'))
		self.assertIsNone(Block.from_str('oak_stairs:half=top').with_state({'half':'bottom'}))
	
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
		self.assertEqual(bc(['oak_stairs:half=bottom', 'oak_stairs:half=top']).remove(bc(['oak_stairs:half=top'])), bc(['oak_stairs:half=bottom']))
		self.assertEqual(bc(['oak_stairs:facing=north:half=top', 'oak_stairs:facing=north:half=bottom']).remove(bc(['oak_stairs:half=bottom'])), bc(['oak_stairs:facing=north:half=top']))