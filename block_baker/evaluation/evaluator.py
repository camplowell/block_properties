from typing import List
from .parser import parse, BinaryOperator, Identity
from core import query

def _or(left:List[str], right:List[str]):
	hold = left.copy()
	hold.extend([item for item in right if item not in left])
	return hold

def _and(left:List[str], right:List[str]):
	return [item for item in left if item in right]

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
	
