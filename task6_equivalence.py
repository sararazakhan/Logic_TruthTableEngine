import re
import itertools

# ==========================================
# 1. AST NODES (From Task 1)
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
# 3. VARIABLE EXTRACTION & EVALUATOR (Tasks 2 & 3)
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

# ==========================================
# 4. TASK 6 IMPLEMENTATION: EQUIVALENCE REPORT
# ==========================================
def report_equivalences(expressions):
    """
    Takes a list of expression strings, evaluates them across all variables,
    and groups those that are logically equivalent.
    """
    print("="*60)
    print("TASK 6: LOGICAL EQUIVALENCE REPORT")
    print("="*60)
    
    parsed_data = []
    all_vars = set()
    
    # 1. Parse all expressions and collect all unique variables
    for expr in expressions:
        ast = Parser(tokenize(expr)).parse()
        vars_in_expr = get_variables(ast)
        all_vars.update(vars_in_expr)
        parsed_data.append((expr, ast))
        
    all_vars = sorted(list(all_vars))
    print(f"All variables involved across expressions: {all_vars}")
    print(f"Total possible assignments (2^{len(all_vars)}): {2**len(all_vars)}\n")
    
    # 2. Generate truth assignments for the combined set of variables
    assignments = [dict(zip(all_vars, combo)) for combo in itertools.product([False, True], repeat=len(all_vars))]
    
    # 3. Evaluate each expression to get its "Truth Signature"
    # A signature is a tuple of boolean results for every assignment row.
    signatures = {}
    for expr, ast in parsed_data:
        sig = tuple(evaluate(ast, env) for env in assignments)
        if sig not in signatures:
            signatures[sig] = []
        signatures[sig].append(expr)
        
    # 4. Print the Results
    print("--- Equivalence Groups ---")
    group_num = 1
    for sig, exprs in signatures.items():
        if len(exprs) > 1:
            print(f"\nGroup {group_num} (Logically Equivalent):")
            for e in exprs:
                print(f"  -> {e}")
            group_num += 1
            
    print("\n--- Unique Expressions (Not equivalent to any other in this list) ---")
    for sig, exprs in signatures.items():
        if len(exprs) == 1:
            print(f"  -> {exprs[0]}")


# ==========================================
# 5. TESTING TASK 6
# ==========================================
if __name__ == "__main__":
    # A list of expressions with 2 and 3 variables.
    # We include known logical equivalences (like Implication and De Morgan's).
    test_expressions = [
        # Group 1: Implication equivalence (3 variables involved overall)
        "A IMPLIES (B AND C)",
        "NOT A OR (B AND C)",
        "(A IMPLIES B) AND (A IMPLIES C)",
        
        # Group 2: Precedence / Bracketing equivalence (3 variables)
        "A AND B OR C",
        "(A AND B) OR C",
        
        # Group 3: De Morgan's Equivalence
        "NOT (A OR B)",
        "(NOT A) AND (NOT B)",
        
        # A unique expression to show it stands alone
        "A AND (B OR C)",
        
        # Another unique expression
        "A <-> B"
    ]

    report_equivalences(test_expressions)
