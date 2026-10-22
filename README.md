# Logic_TruthTableEngine
A Recursive-Descent Parser and Automated Evaluator for Propositional Symbolic Logic
## Objective
The objective of this project is to develop a Python-based Logic and Truth-Table Engine that parses propositional logic expressions and automatically generates their truth tables. The system aims to classify expressions as tautologies, contradictions, or contingencies, while strictly separating the parsing logic from the evaluation logic. Additionally, it seeks to automate the verification of De Morgan's Laws and identify logical equivalences across expressions.

## Project Structure
* `task1_parser.py`: Recursive-descent parser and AST nodes.
* `task2_variables.py`: Variable extraction and truth assignment generation.
* `task3_evaluator.py`: AST evaluator and Markdown table formatter.
* `task4_classifier.py`: Logic to classify tautologies/contradictions.
* `task5_de_morgan.py`: Automated De Morgan's Law verifier.
* `task6_equivalence.py`: Cross-expression equivalence reporter.
* `main.py`: The main execution script.

## Write-up: Recursive-Descent Parsing and Precedence
A Recursive-Descent Parser reads input token by token and recursively evaluates nested structures. 
Why Precedence Matters: In logic, operators have an order of operations. If precedence is ignored, `A OR B AND C` could be interpreted as `(A OR B) AND C`, yielding an incorrect truth table. Our parser respects the standard hierarchy: NOT > AND > OR > IMPLIES > BICONDITIONAL. By structuring the parsing functions from lowest precedence (`parse_biconditional`) to highest (`parse_atom`), the parser correctly groups operations. Parentheses override this by recursively calling the lowest-precedence function when encountered.

## Truth Table Report
*(Run main.py to generate tables. Example below)*
### 1. A OR NOT A (Tautology)
| A | Result |
|---|---|
| F | T |
| T | T |

### 2. A AND NOT A (Contradiction)
| A | Result |
|---|---|
| F | F |
| T | F |

### 3. A IMPLIES B (Contingency)
| A | B | Result |
|---|---|---|
| F | F | T |
| F | T | T |
| T | F | F |
| T | T | T |

### 4. A AND (B OR C) (Contingency)
| A | B | C | Result |
|---|---|---|---|
| F | F | F | F |
| F | F | T | F |
| F | T | F | F |
| F | T | T | F |
| T | F | F | F |
| T | F | T | T |
| T | T | F | T |
| T | T | T | T |
