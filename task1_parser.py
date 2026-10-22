import re

# ==========================================
# 1. ABSTRACT SYNTAX TREE (AST) NODES
# ==========================================
class Node:
    """Base class for AST nodes"""
    pass

class VarNode(Node):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class NotNode(Node):
    def __init__(self, operand):
        self.operand = operand
    def __repr__(self):
        return f"(NOT {self.operand})"

class BinOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

# ==========================================
# 2. LEXER (TOKENIZER)
# ==========================================
def tokenize(expression):
    """
    Converts the raw text into a list of tokens.
    Also standardizes symbols (e.g., & -> AND, -> -> IMPLIES)
    """
    # Standardize symbols to words for easier parsing
    expr = expression.replace('&', ' AND ').replace('|', ' OR ')
    expr = expr.replace('~', ' NOT ').replace('->', ' IMPLIES ')
    expr = expr.replace('<->', ' BICONDITIONAL ')
    
    # Regex to find words, parentheses, and ignore extra spaces
    tokens = re.findall(r'\bAND\b|\bOR\b|\bNOT\b|\bIMPLIES\b|\bBICONDITIONAL\b|[A-Za-z][A-Za-z0-9_]*|[()]', expr)
    return tokens

# ==========================================
# 3. PARSER (Recursive Descent)
# ==========================================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        """Look at the current token without consuming it"""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        """Return the current token and advance the pointer"""
        token = self.peek()
        self.pos += 1
        return token

    def parse(self):
        """Entry point for parsing"""
        if not self.tokens:
            return None
        ast = self.parse_biconditional() # Start with lowest precedence
        if self.pos < len(self.tokens):
            raise SyntaxError(f"Unexpected token at end: {self.peek()}")
        return ast

    # --- Precedence Levels (Lowest to Highest) ---

    def parse_biconditional(self):
        left = self.parse_implication()
        while self.peek() == 'BICONDITIONAL':
            op = self.consume()
            right = self.parse_implication()
            left = BinOpNode(left, op, right)
        return left

    def parse_implication(self):
        left = self.parse_or()
        if self.peek() == 'IMPLIES': # Right-associative
            op = self.consume()
            right = self.parse_implication()
            return BinOpNode(left, op, right)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.peek() == 'OR':
            op = self.consume()
            right = self.parse_and()
            left = BinOpNode(left, op, right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.peek() == 'AND':
            op = self.consume()
            right = self.parse_not()
            left = BinOpNode(left, op, right)
        return left

    def parse_not(self):
        if self.peek() == 'NOT':
            op = self.consume()
            operand = self.parse_not() # NOT is right-associative
            return NotNode(operand)
        return self.parse_atom()

    # --- Highest Precedence: Atoms and Bracketing ---

    def parse_atom(self):
        token = self.consume()
        if token == '(':
            # Recursively call the lowest precedence function to handle grouped logic
            expr = self.parse_biconditional() 
            if self.consume() != ')':
                raise SyntaxError("Expected closing parenthesis ')'")
            return expr
        elif token in ['AND', 'OR', 'IMPLIES', 'BICONDITIONAL', ')']:
            raise SyntaxError(f"Unexpected operator: {token}")
        elif token is None:
            raise SyntaxError("Unexpected end of expression")
        else:
            # It's a variable (e.g., 'A', 'B', 'P1')
            return VarNode(token)

# Test cases to prove precedence and bracketing work
expressions_to_test = [
    "A OR B AND C",       # Precedence: AND should group first
    "(A OR B) AND C",     # Bracketing: OR should group first
    "NOT A AND B",        # Precedence: NOT should apply only to A
    "A -> B <-> C",       # Precedence: -> binds tighter than <->
    "A OR NOT (B AND C)"  # Complex nesting
]

for expr in expressions_to_test:
    tokens = tokenize(expr)
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"Original: {expr}")
    print(f"Parsed AST: {ast}")
    print("-" * 40)
