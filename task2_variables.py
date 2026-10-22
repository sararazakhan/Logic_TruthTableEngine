import re
import itertools

# ==========================================
# 1. AST NODES (From Task 1)
# ==========================================
class Node:
    pass

class VarNode(Node):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class NotNode(Node):
    def __init__(self, operand):
        self.operand = operand

class BinOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

# ==========================================
# 2. PARSER (Simplified version from Task 1)
# ==========================================
def tokenize(expression):
    expr = expression.replace('&', ' AND ').replace('|', ' OR ')
    expr = expr.replace('~', ' NOT ').replace('->', ' IMPLIES ')
    expr = expr.replace('<->', ' BICONDITIONAL ')
    return re.findall(r'\bAND\b|\bOR\b|\bNOT\b|\bIMPLIES\b|\bBICONDITIONAL\b|[A-Za-z][A-Za-z0-9_]*|[()]', expr)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def consume(self):
        token = self.peek()
        self.pos += 1
        return token
    def parse(self):
        if not self.tokens: return None
        ast = self.parse_biconditional()
        return ast
    def parse_biconditional(self):
        left = self.parse_implication()
        while self.peek() == 'BICONDITIONAL':
            op = self.consume()
            right = self.parse_implication()
            left = BinOpNode(left, op, right)
        return left
    def parse_implication(self):
        left = self.parse_or()
        if self.peek() == 'IMPLIES':
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
            self.consume()
            return NotNode(self.parse_not())
        return self.parse_atom()
    def parse_atom(self):
        token = self.consume()
        if token == '(':
            expr = self.parse_biconditional()
            self.consume() # consume ')'
            return expr
        return VarNode(token)


# ==========================================
# 3. TASK 2 IMPLEMENTATION
# ==========================================

def get_variables(ast):
    """
    Traverses the AST and extracts all distinct variable names.
    Returns a sorted list.
    """
    variables = set()
    
    def traverse(node):
        if isinstance(node, VarNode):
            variables.add(node.name)
        elif isinstance(node, NotNode):
            traverse(node.operand)
        elif isinstance(node, BinOpNode):
            traverse(node.left)
            traverse(node.right)
            
    traverse(ast)
    return sorted(list(variables))

def generate_assignments(variables):
    """
    Generates all 2^n truth-value assignments for the given variables.
    Returns a list of dictionaries where keys are variables and values are booleans.
    """
    n = len(variables)
    assignments = []
    
    # itertools.product([False, True], repeat=n) yields tuples like:
    # (False, False), (False, True), (True, False), (True, True)
    for combination in itertools.product([False, True], repeat=n):
        # Create a dictionary mapping variable names to their boolean value
        env = dict(zip(variables, combination))
        assignments.append(env)
        
    return assignments

# ==========================================
# 4. VERIFICATION / TESTING
# ==========================================
if __name__ == "__main__":
    # Test expression with 3 variables (A, B, C) and a duplicate 'A'
    expr = "A AND (B OR NOT C) -> A"
    
    print(f"Original Expression: {expr}")
    
    # 1. Parse the expression
    tokens = tokenize(expr)
    parser = Parser(tokens)
    ast = parser.parse()
    
    # 2. Identify variables (Task 2, Part 1)
    variables = get_variables(ast)
    print(f"Distinct Variables found: {variables}")
    print(f"Number of variables (n): {len(variables)}")
    print(f"Expected assignments (2^n): 2^{len(variables)} = {2**len(variables)}")
    
    # 3. Generate assignments (Task 2, Part 2)
    assignments = generate_assignments(variables)
    
    print("\nGenerated Truth-Value Assignments:")
    for i, env in enumerate(assignments, 1):
        print(f"Row {i}: {env}")
