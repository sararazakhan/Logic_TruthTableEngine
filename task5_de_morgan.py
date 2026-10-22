import re
import itertools

# ==========================================
# 1. AST NODES (From Task 1)
# ==========================================
class Node: pass
class VarNode(Node):
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name
class NotNode(Node):
    def __init__(self, operand): self.operand = operand
    def __repr__(self): return f"(NOT {self.operand})"
class BinOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self): return f"({self.left} {self.op} {self.right})"

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
# 3. UTILITIES & EVALUATOR (From Tasks 2 & 3)
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
# 4. TASK 5 IMPLEMENTATION: DE MORGAN'S ENGINE
# ==========================================

def negate_ast(node):
    """Step 1: Wrap the entire AST in a NOT node."""
    return NotNode(node)

def simplify_negation(node):
    """
    Step 2: Recursively push NOT inward using De Morgan's Laws.
    """
    # If the node is a NOT, we check what's inside it
    if isinstance(node, NotNode):
        inner = node.operand
        
        # Base case: NOT applied directly to a variable (e.g., NOT A)
        if isinstance(inner, VarNode):
            return node 
            
        # Double Negation: NOT (NOT A) => A
        elif isinstance(inner, NotNode):
            return simplify_negation(inner.operand)
            
        # De Morgan's Laws: NOT applied to an AND/OR
        elif isinstance(inner, BinOpNode):
            if inner.op == 'AND':
                # NOT (A AND B) => (NOT A) OR (NOT B)
                left_simp = simplify_negation(NotNode(inner.left))
                right_simp = simplify_negation(NotNode(inner.right))
                return BinOpNode(left_simp, 'OR', right_simp)
                
            elif inner.op == 'OR':
                # NOT (A OR B) => (NOT A) AND (NOT B)
                left_simp = simplify_negation(NotNode(inner.left))
                right_simp = simplify_negation(NotNode(inner.right))
                return BinOpNode(left_simp, 'AND', right_simp)
    
    # If it's not a NOT node (e.g., we are deep in the tree), just return it
    return node

def are_equivalent(ast1, ast2):
    """
    Step 3: Confirm row-by-row that the two ASTs yield the same result.
    """
    vars1 = get_variables(ast1)
    vars2 = get_variables(ast2)
    all_vars = sorted(list(set(vars1 + vars2)))
    
    for combo in itertools.product([False, True], repeat=len(all_vars)):
        env = dict(zip(all_vars, combo))
        val1 = evaluate(ast1, env)
        val2 = evaluate(ast2, env)
        
        # Print row-by-row confirmation
        row_str = ", ".join([f"{k}={'T' if v else 'F'}" for k, v in env.items()])
        print(f"| {row_str:<20} | {'T' if val1 else 'F':<12} | {'T' if val2 else 'F':<12} | {'Yes' if val1 == val2 else 'NO':<5} |")
        
        if val1 != val2:
            return False
            
    return True

# ==========================================
# 5. TESTING TASK 5
# ==========================================
def run_dm_check(expression):
    print(f"\nOriginal Expression: {expression}")
    
    # 1. Parse original
    ast_original = Parser(tokenize(expression)).parse()
    
    # 2. Negate
    ast_negated = negate_ast(ast_original)
    print(f"Negated AST:          {ast_negated}")
    
    # 3. Simplify
    ast_simplified = simplify_negation(ast_negated)
    print(f"Simplified Negation:  {ast_simplified}")
    
    # 4. Check Equivalence Row-by-Row
    print("\nRow-by-Row Verification:")
    print(f"| {'Assignment':<20} | {'Negated':<12} | {'Simplified':<12} | {'Match':<5} |")
    print(f"|{'-'*22}|{'-'*14}|{'-'*14}|{'-'*7}|")
    
    is_equiv = are_equivalent(ast_negated, ast_simplified)
    
    print(f"\nConclusion: The two expressions are {'EQUIVALENT' if is_equiv else 'NOT EQUIVALENT'}.")

if __name__ == "__main__":
    # Test Case 1: De Morgan on AND
    run_dm_check("A AND B")
    
    # Test Case 2: De Morgan on OR
    run_dm_check("A OR B")
    
    # Test Case 3: Complex Expression
    run_dm_check("A AND (B OR C)")
