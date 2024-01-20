from typing import Dict, List

from .lexer import Token, lex

class BinaryOperator:
	def __init__(self, left, op, right):
		self.left = left
		self.op = op
		self.right = right

	def __repr__(self) -> str:
		return "{}({}, {})".format(self.op, self.left, self.right)

class Identity:
	def __init__(self, value):
		self.value = value

	def __repr__(self) -> str:
		return "{}".format(self.value)

def _parse(tokens:List[Token]):
	def _eat(*values):
		expected = "\nExpected one of: '{}')".format("', '".join(values))
		if not tokens:
			raise ValueError('Unexpected end of string{}'.format(expected))
		token = tokens[0]
		if token.type not in values:
			raise ValueError("Unexpected token: '{}'{}".format(token.value, expected))
		return tokens.pop(0)
	def _expr() -> Dict[str, str]:
		return _combine()
	def _val():
		if tokens[0].type == '(':
			_eat('(')
			expr = _expr()
			_eat(')')
			return expr
		if tokens[0].type == 'IDENT':
			return Identity(_eat('IDENT').token)
		raise ValueError("Malformed value '{}'".format(tokens[0].token))
	def _combine():
		active = _val()
		while tokens and tokens[0].type in ['and', 'or', 'xor', 'sub']:
			active = BinaryOperator(active, _eat('and', 'or', 'xor', 'sub').type, _val())
		return active
	
	return _expr()

def parse(expression:str):
	return _parse(lex(expression))