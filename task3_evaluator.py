import re
import itertools

# ==========================================
# 1. AST NODES
# ==========================================
class Node: pass
class VarNode(Node):
    def __init__(self, name): self.name = name
class NotNode(Node):
    def __init__(self, operand): self.operand = operand
class BinOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

# ==========================================
# 2. PARSER & TOKENIZER (From Task 1)
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
    def peek(self): return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def consume(self):
        token = self.peek()
        self.pos += 1
        return token
    def parse(self):
        if not self.tokens: return None
        return self.parse_biconditional()
    def parse_biconditional(self):
        left = self.parse_implication()
        while self.peek() == 'BICONDITIONAL':
            op = self.consume()
            left = BinOpNode(left, op, self.parse_implication())
        return left
    def parse_implication(self):
        left = self.parse_or()
        if self.peek() == 'IMPLIES':
            op = self.consume()
            return BinOpNode(left, op, self.parse_implication())
        return left
    def parse_or(self):
        left = self.parse_and()
        while self.peek() == 'OR':
            op = self.consume()
            left = BinOpNode(left, op, self.parse_and())
        return left
    def parse_and(self):
        left = self.parse_not()
        while self.peek() == 'AND':
            op = self.consume()
            left = BinOpNode(left, op, self.parse_not())
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
            self.consume() # ')'
            return expr
        return VarNode(token)

# ==========================================
# 3. VARIABLE EXTRACTION & ASSIGNMENTS (From Task 2)
# ==========================================
def get_variables(ast):
    variables = set()
    def traverse(node):
        if isinstance(node, VarNode): variables.add(node.name)
        elif isinstance(node, NotNode): traverse(node.operand)
        elif isinstance(node, BinOpNode):
            traverse(node.left)
            traverse(node.right)
    traverse(ast)
    return sorted(list(variables))

def generate_assignments(variables):
    return [dict(zip(variables, combo)) for combo in itertools.product([False, True], repeat=len(variables))]

# ==========================================
# 4. EVALUATOR & FORMATTER (Task 3)
# ==========================================
def evaluate(node, assignment):
    """Recursively evaluates the AST given a specific variable assignment."""
    if isinstance(node, VarNode):
        return assignment[node.name]
    elif isinstance(node, NotNode):
        return not evaluate(node.operand, assignment)
    elif isinstance(node, BinOpNode):
        left = evaluate(node.left, assignment)
        right = evaluate(node.right, assignment)
        
        if node.op == 'AND': return left and right
        elif node.op == 'OR': return left or right
        elif node.op == 'IMPLIES': return (not left) or right
        elif node.op == 'BICONDITIONAL': return left == right
        
    raise ValueError("Unknown AST Node")

def print_truth_table(expression):
    """Parses, evaluates, and prints a Markdown formatted truth table."""
    # 1. Parse
    tokens = tokenize(expression)
    ast = Parser(tokens).parse()
    variables = get_variables(ast)
    
    # 2. Generate Assignments
    assignments = generate_assignments(variables)
    
    print(f"Expression: {expression}")
    print("-" * 40)
    
    # 3. Format Markdown Table Header
    header = " | ".join(variables) + " | Result"
    separator = "|".join(["---"] * (len(variables) + 1))
    print(f"| {header} |")
    print(f"|{separator}|")
    
    # 4. Evaluate and Format Rows
    for env in assignments:
        # Evaluate expression for this row
        result = evaluate(ast, env)
        
        # Format booleans as T/F strings
        row_values = " | ".join(["T" if env[var] else "F" for var in variables])
        result_str = "T" if result else "F"
        
        print(f"| {row_values} | {result_str} |")
    print("\n")

# ==========================================
# 5. TESTING TASK 3
# ==========================================
if __name__ == "__main__":
    # Test 1: Basic AND, OR, NOT
    print_truth_table("A AND B")
    
    # Test 2: Complex expression with Implication and Bracketing
    print_truth_table("(A OR B) IMPLIES NOT C")
    
    # Test 3: Tautology (Always True)
    print_truth_table("A OR NOT A")
