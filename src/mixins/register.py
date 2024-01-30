from core.tag import TagLibrary
from .state_mixin import StateTag

def register_all_mixins(library:TagLibrary):
	register_stair_mixins(library)
	register_slab_mixins(library)


def register_stair_mixins(library:TagLibrary):
	get_stairs = lambda:library.get('stairs').get()
	library.register_mixin(StateTag('stairs/solid/top', get_stairs).add_state({'half':'top'}))
	library.register_mixin(StateTag('stairs/solid/bottom', get_stairs).add_state({'half':'bottom'}))
	directions = ['north', 'east', 'south', 'west']
	for l, s, r in [(directions[i-1], directions[i], directions[(i+1) % len(directions)]) for i in range(len(directions))]:
		tag = StateTag(f'stairs/solid/{s}', get_stairs)
		tag.add_state({'shape':'straight',    'facing':s, 'half':'bottom'})
		tag.add_state({'shape':'straight',    'facing':s, 'half':'top'})
		tag.add_state({'shape':'inner_left',  'facing':s, 'half':'bottom'})
		tag.add_state({'shape':'inner_left',  'facing':s, 'half':'top'})
		tag.add_state({'shape':'inner_left',  'facing':r, 'half':'bottom'})
		tag.add_state({'shape':'inner_left',  'facing':r, 'half':'top'})
		tag.add_state({'shape':'inner_right', 'facing':l, 'half':'bottom'})
		tag.add_state({'shape':'inner_right', 'facing':l, 'half':'top'})
		tag.add_state({'shape':'inner_right', 'facing':s, 'half':'bottom'})
		tag.add_state({'shape':'inner_right', 'facing':s, 'half':'top'})
		library.register_mixin(tag)

def register_slab_mixins(library:TagLibrary):
	get_slabs = lambda:library.get('slab').get()
	library.register_mixin(StateTag('slab/bottom', get_slabs).add_state({'type':'bottom'}))
	library.register_mixin(StateTag('slab/top', get_slabs).add_state({'type':'top'}))
	library.register_mixin(StateTag('slab/half', get_slabs).add_state({'type':'bottom'}).add_state({'type':'top'}))
	library.register_mixin(StateTag('slab/double', get_slabs).add_state({'type':'double'}))