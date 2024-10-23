#Data Structure AST 
import ast
import operator
from collections import Counter
OPERATORS = {
    'and': operator.and_,
    'or': operator.or_,
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le
}

class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.node_type = node_type  # "operator" or "operand"
        self.value = value  # Value like "age > 30" or "AND"
        self.left = left  # Left child node
        self.right = right  # Right child node

    def to_dict(self):
        return {
            'type': self.node_type,
            'value': self.value,
            'left': self.left.to_dict() if self.left else None,
            'right': self.right.to_dict() if self.right else None
        }

def parse_expression(expr):
    """
    Recursively parse the rule expression and return an AST as a Node object.
    """
    if isinstance(expr, ast.BoolOp):
        operator_type = 'and' if isinstance(expr.op, ast.And) else 'or'
        left = parse_expression(expr.values[0])
        right = parse_expression(expr.values[1])
        return Node('operator', value=operator_type, left=left, right=right)

    elif isinstance(expr, ast.Compare):
        left_operand = expr.left.id  # e.g., "age"
        right_operand = expr.comparators[0].n if isinstance(expr.comparators[0], ast.Num) else expr.comparators[0].s
        operator_symbol = expr.ops[0]

        if isinstance(operator_symbol, ast.Gt):
            operator_type = '>'
        elif isinstance(operator_symbol, ast.Lt):
            operator_type = '<'
        elif isinstance(operator_symbol, ast.Eq):
            operator_type = '=='
        elif isinstance(operator_symbol, ast.NotEq):  
            operator_type = '!='
        elif isinstance(operator_symbol, ast.GtE):
            operator_type = '>='
        elif isinstance(operator_symbol, ast.LtE):
            operator_type = '<='
        else:
            raise ValueError(f"Unsupported comparison operator: {operator_symbol}")

        condition = f"{left_operand} {operator_type} {right_operand}"
        return Node('operand', value=condition)

def create_rule(rule_string):
    """
    Parse a rule string and build the corresponding AST.
    """
    rule_string = rule_string.replace('AND', 'and').replace('OR', 'or').replace('=', '==')
    parsed_rule = ast.parse(rule_string, mode='eval')
    return parse_expression(parsed_rule.body)
def combine_rules(rule_strings):
    """
    Combines multiple rule strings into a single AST using a most frequent operator heuristic.
    """
    asts = [create_rule(rule) for rule in rule_strings]
    operator_count = Counter()
    for rule_string in rule_strings:
        operator_count['and'] += rule_string.lower().count('and')
        operator_count['or'] += rule_string.lower().count('or')

    combining_operator = 'and' if operator_count['and'] >= operator_count['or'] else 'or'
    combined_ast = asts[0]
    for ast in asts[1:]:
        combined_ast = Node('operator', value=combining_operator, left=combined_ast, right=ast)

    return combined_ast

def evaluate_node(node, data):
    """
    Recursively evaluate an AST node against the given data.
    """
    if node.node_type == 'operand':
        left_operand, operator_symbol, right_operand = node.value.split()
        left_value = data[left_operand]

        if right_operand.isdigit():
            right_value = int(right_operand)
        else:
            right_value = right_operand.strip("'")

        if operator_symbol == '>':
            return left_value > right_value
        elif operator_symbol == '<':
            return left_value < right_value
        elif operator_symbol == '==':
            return left_value == right_value
        elif operator_symbol == '!=':
            return left_value != right_value
        elif operator_symbol == '>=':
            return left_value >= right_value
        elif operator_symbol == '<=':
            return left_value <= right_value
        else:
            raise ValueError(f"Unsupported operator: {operator_symbol}")

    elif node.node_type == 'operator':
        left_result = evaluate_node(node.left, data)
        right_result = evaluate_node(node.right, data)

        if node.value == 'and':
            return left_result and right_result
        elif node.value == 'or':
            return left_result or right_result
        else:
            raise ValueError(f"Unsupported logical operator: {node.value}")

def evaluate_rule(ast_root, data):
    """
    Evaluate the entire AST rule against the provided data.
    """
    return evaluate_node(ast_root, data)
def dict_to_ast(node_dict):
    if not node_dict:
        return None

    node = Node(node_dict['type'], node_dict.get('value'))
    node.left = dict_to_ast(node_dict.get('left'))
    node.right = dict_to_ast(node_dict.get('right'))

    return node

