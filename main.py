import re
import itertools

# ==========================================
# 1. ABSTRACT SYNTAX TREE (AST)
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
# 2. THE PARSER (Syntax)
# Separated entirely from the evaluator
# ==========================================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def tokenize(self, expression):
        expr = expression.replace('&', ' AND ').replace('|', ' OR ')
        expr = expr.replace('~', ' NOT ').replace('->', ' IMPLIES ')
        expr = expr.replace('<->', ' BICONDITIONAL ')
        return re.findall(r'\bAND\b|\bOR\b|\bNOT\b|\bIMPLIES\b|\bBICONDITIONAL\b|[A-Za-z][A-Za-z0-9_]*|[()]', expr)

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
# 3. THE EVALUATOR (Semantics)
# Separated entirely from the parser
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

def evaluate(node, assignment):
    if isinstance(node, VarNode): return assignment[node.name]
    elif isinstance(node, NotNode): return not evaluate(node.operand, assignment)
    elif isinstance(node, BinOpNode):
        left = evaluate(node.left, assignment)
        right = evaluate(node.right, assignment)
        if node.op == 'AND': return left and right
        elif node.op == 'OR': return left or right
        elif node.op == 'IMPLIES': return (not left) or right
        elif node.op == 'BICONDITIONAL': return left == right
    raise ValueError("Unknown AST Node")

def classify_expression(results):
    if all(results): return "Tautology"
    elif not any(results): return "Contradiction"
    else: return "Contingency"


# ==========================================
# 4. MAIN EXECUTION (Generating Report)
# ==========================================
if __name__ == "__main__":
    # 4 Expressions required: 1 Tautology, 1 Contradiction, 2 Others
    expressions = [
        "A OR NOT A",               # Tautology
        "A AND NOT A",              # Contradiction
        "A IMPLIES B",              # Contingency
        "A AND (B OR C)"            # Contingency (3 variables)
    ]

    for expr in expressions:
        parser = Parser([])
        tokens = parser.tokenize(expr)
        ast = Parser(tokens).parse()
        
        variables = get_variables(ast)
        assignments = [dict(zip(variables, combo)) for combo in itertools.product([False, True], repeat=len(variables))]
        
        results = [evaluate(ast, env) for env in assignments]
        classification = classify_expression(results)
        
        # Print Markdown Table
        print(f"\n**Expression:** `{expr}`")
        print(f"**Classification:** {classification}\n")
        
        header = " | ".join(variables) + " | Result"
        separator = "|".join(["---"] * (len(variables) + 1))
        print(f"| {header} |")
        print(f"|{separator}|")
        
        for env, res in zip(assignments, results):
            row_values = " | ".join(["T" if env[var] else "F" for var in variables])
            print(f"| {row_values} | {'T' if res else 'F'} |")
