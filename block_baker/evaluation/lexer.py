import re

_PATTERNS = [
	[r'^\s+', None],
	[r'[a-zA-Z]+([/:\-_][a-zA-Z0-9]+)*', 'IDENT'],
	[r'\(', '('],
	[r'\)', ')'],
	[r'\|', 'or'],
	[r'\&', 'and'],
	[r'\^', 'xor'],
	[r'\-', 'sub']
]

class Token:
	def __init__(self, type_:None|str, token:str) -> None:
		self.type = type_
		self.token = token
	
	def __str__(self) -> str:
		return "'{}'".format(self.token)
	def __repr__(self) -> str:
		return "'{}'".format(self.token)


def _findNext(formula:str):
	for pattern, type_ in _PATTERNS:
			result = re.match(pattern, formula)
			if result:
				text = result.group()
				formula = formula[result.endpos:]
				return len(text), Token(type_, text)
	raise ValueError("Unknown token: '{}'".format(formula))

def lex(formula:str):
	tokens = []
	while formula:
		inc, token = _findNext(formula)
		formula = formula[inc:]
		if token.type != None:
			tokens.append(token)
	return tokens