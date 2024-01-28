from core.block import BlockCollection
from core.tag import EnumTag, TagLibrary
from evaluation.parser import parse, BinaryOperator, Identity

def _union(left:BlockCollection, right:BlockCollection):
	return left.insert(right)

def _difference(left:BlockCollection, right:BlockCollection):
	return left.remove(right)

def _intersection(left:BlockCollection, right:BlockCollection):
	return left.intersection(right)

def _xor(left:BlockCollection, right:BlockCollection):
	return left.union(right) - left.intersection(right)

def _evaluateIdentity(ident:Identity, library:TagLibrary):
	tag = library.get(ident.tag)
	if isinstance(tag, EnumTag) and ident.value:
		return tag.get(ident.value)
	else:
		return tag.get()
		
def _evaluateOperator(op: BinaryOperator, library:TagLibrary):
	left = evaluate(op.left, library)
	right = evaluate(op.right, library)
	result = {
		'union': _union,
		'difference': _difference,
		'intersection': _intersection,
		'xor': _xor
	}[op.op](left, right)
	return result

def evaluate(expression, library:TagLibrary):
	if isinstance(expression, str):
		expression = parse(expression)
	if isinstance(expression, BinaryOperator):
		return _evaluateOperator(expression, library)
	elif isinstance(expression, Identity):
		return _evaluateIdentity(expression, library)
	else: # BlockCollection
		return expression