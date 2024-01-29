import unittest
from core.block import BlockCollection

from core.tag import TagLibrary


class TestTag(unittest.TestCase):
	def test_tag_preservation(self):
		library = TagLibrary()
		stairs = library.create_bool('stairs')
		collection = BlockCollection.from_strings(['oak_stairs', 'birch_stairs'])
		stairs.add(collection)
		self.assertEquals(library.get('stairs').get(), collection)
	
	def test_tag_bubble_simple(self):
		library = TagLibrary()
		collection = BlockCollection.from_strings(['oak_stairs', 'birch_stairs'])
		library.create_bool('stairs')
		library.create_bool('stairs/wood').add(collection)
		self.assertEqual(library.get('stairs').get(), collection)
	
	def test_tag_bubble_enum(self):
		library = TagLibrary()
		collection = BlockCollection.from_strings(['oak_stairs', 'birch_stairs'])

		enum = library.create_enum('enum', ['foo', 'bar'])
		enum.add('foo', collection)
		bool_child = library.create_bool('enum/bool')
		bool_child.add(collection)
		self.assertEqual(library.get('enum/bool').get(), collection)

	def test_tag_bubble_err(self):
		library = TagLibrary()
		collection = BlockCollection.from_strings(['oak_stairs', 'birch_stairs'])

		library.create_enum('enum', ['foo', 'bar'])
		bool_child = library.create_bool('enum/bool')
		self.assertRaises(RuntimeError, lambda: bool_child.add(collection))