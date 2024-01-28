import unittest
from core.block import BlockCollection

from core.tag import TagLibrary
from mixins.state_mixin import StateTag

class TestStateMixin(unittest.TestCase):
	def test_mixin_tag(self):
		library = TagLibrary()
		bottom_mixin = StateTag('stairs/solid/bottom', lambda:library.get('stairs').get()).add_state({'half':['bottom']})
		library.register_mixin(bottom_mixin)

		stairs = library.create_bool('stairs')
		collection = BlockCollection.from_strings(['oak_stairs'])
		stairs.add(collection)
		
		self.assertEqual(library.get('stairs/solid/bottom').get(), BlockCollection.from_strings(['oak_stairs:half=bottom']))