from typing import List
from .parser import parse, BinaryOperator, Identity
from core import query

def childOf(a, b):
	return a.startswith(b) and a[len(b)] in [":", ","]

def contains(collection, search):
	for item in collection:
		if item == search or childOf(item, search):
			return True
	return False

def _or(left:List[str], right:List[str]):
	hold = left.copy()
	# Convert items in left to parent if the parent is in right
	for i, item in enumerate(hold):
		for rightItem in right:
			if childOf(item, rightItem):
				hold[i] = rightItem
	# Add items that are in right but not left
	hold.extend([item for item in right if not contains(left, item)])
	return hold

def _and(left:List[str], right:List[str]):
	result = []
	for l in left:
		for r in right:
			if l == r or childOf(l, r):
				result.append(l)
			elif childOf(r, l):
				result.append(r)
	return result

def _sub(left:List[str], right:List[str]):
	return [item for item in left if item not in right]

def _xor(left:List[str], right:List[str]):
	leftOnly = _sub(left, right)
	rightOnly = _sub(right, left)
	return _or(leftOnly, rightOnly)

def _evaluateOperator(expr:BinaryOperator):
	left = evaluate(expr.left)
	right = evaluate(expr.right)
	return {
		'or': _or,
		'and': _and,
		'xor': _xor,
		'sub': _sub
	}[expr.op](left, right)

def _evaluateIdentity(expr:Identity):
	return query.get_blocks(expr.value)

def evaluate(expression:str):
	if isinstance(expression, str):
		expression = parse(expression)
	if isinstance(expression, BinaryOperator):
		return _evaluateOperator(expression)
	elif isinstance(expression, Identity):
		return _evaluateIdentity(expression)
	
