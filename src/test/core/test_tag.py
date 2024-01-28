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