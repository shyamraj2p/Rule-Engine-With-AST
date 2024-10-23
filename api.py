from flask import Flask, request, jsonify, render_template
import ast
import operator
import sqlite3
from collections import Counter

app = Flask(__name__)


# Initialize of database
def init_db():
    conn = sqlite3.connect('rules.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rules (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, rule TEXT, ast TEXT)''')
    conn.commit()
    conn.close()

def store_rule(name, rule_string, ast):
    conn = sqlite3.connect('rules.db')
    c = conn.cursor()
    c.execute("INSERT INTO rules (name, rule, ast) VALUES (?, ?, ?)", (name, rule_string, str(ast)))
    rule_id = c.lastrowid
    conn.commit()
    conn.close()
    return rule_id

def get_all_rules():
    conn = sqlite3.connect('rules.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rules")
    rules = c.fetchall()
    conn.close()
    return rules

# APIS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_rule', methods=['POST'])
def create_rule_api():
    rule_string = request.json['rule']
    name = request.json['name']
    ast = create_rule(rule_string)
    rule_id = store_rule(name, rule_string, ast.to_dict())
    return jsonify({'rule_id': rule_id, 'name': name, 'ast': ast.to_dict()})

@app.route('/api/view_rules', methods=['GET'])
def view_rules():
    rules = get_all_rules()
    return jsonify(rules)

@app.route('/api/combine_rules', methods=['POST'])
def combine_rules_api():
    rule_ids = request.json['rule_ids']
    names = request.json['names']  

    conn = sqlite3.connect('rules.db')
    c = conn.cursor()
    c.execute("SELECT rule FROM rules WHERE id IN (?, ?)", rule_ids)
    rule_strings = [row[0] for row in c.fetchall()]
    conn.close()

    combined_ast = combine_rules(rule_strings)
    combined_rule = f"({rule_strings[0]}) AND ({rule_strings[1]})"
    combined_rule_id = store_rule(names, combined_rule, combined_ast.to_dict())
    return jsonify({'combined_rule_id': combined_rule_id, 'names': names, 'combined_ast': combined_ast.to_dict()})

@app.route('/api/evaluate_rule', methods=['POST'])
def evaluate_rule_api():
    rule_id = request.json['rule_id']
    data = request.json['data']

    conn = sqlite3.connect('rules.db')
    c = conn.cursor()
    c.execute("SELECT ast FROM rules WHERE id=?", (rule_id,))
    ast_dict = eval(c.fetchone()[0])  
    conn.close()

    ast = dict_to_ast(ast_dict)
    result = evaluate_rule(ast, data)
    return jsonify({'result': result})


def dict_to_ast(ast_dict):
    node = Node(ast_dict['type'], ast_dict['value'])
    if ast_dict['left']:
        node.left = dict_to_ast(ast_dict['left'])
    if ast_dict['right']:
        node.right = dict_to_ast(ast_dict['right'])
    return node
# Define operator mappings for AST construction
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
        self.node_type = node_type
        self.value = value
        self.left = left
        self.right = right

    def to_dict(self):
        return {
            'type': self.node_type,
            'value': self.value,
            'left': self.left.to_dict() if self.left else None,
            'right': self.right.to_dict() if self.right else None
        }

def parse_expression(expr):
    if isinstance(expr, ast.BoolOp):
        operator_type = 'and' if isinstance(expr.op, ast.And) else 'or'
        left = parse_expression(expr.values[0])
        right = parse_expression(expr.values[1])
        return Node('operator', value=operator_type, left=left, right=right)

    elif isinstance(expr, ast.Compare):
        left_operand = expr.left.id
        right_operand = expr.comparators[0].n if isinstance(expr.comparators[0], ast.Num) else expr.comparators[0].s
        operator_symbol = expr.ops[0]

        operator_type = {
            ast.Gt: '>', ast.Lt: '<', ast.Eq: '==', ast.NotEq: '!=',
            ast.GtE: '>=', ast.LtE: '<='
        }.get(type(operator_symbol))

        condition = f"{left_operand} {operator_type} {right_operand}"
        return Node('operand', value=condition)

def create_rule(rule_string):
    rule_string = rule_string.replace('AND', 'and').replace('OR', 'or').replace('=', '==')
    parsed_rule = ast.parse(rule_string, mode='eval')
    return parse_expression(parsed_rule.body)

def combine_rules(rule_strings):
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
    left_operand, operator_symbol, right_operand = node.value.split()
    if left_operand not in data:
        return {'error': f"'{left_operand}' is not found in the provided data."}
    left_value = data[left_operand]
    right_value = int(right_operand) if right_operand.isdigit() else right_operand.strip("'")

    return {
        '>': left_value > right_value, '<': left_value < right_value,
        '==': left_value == right_value, '!=': left_value != right_value,
        '>=': left_value >= right_value, '<=': left_value <= right_value
    }[operator_symbol]

def evaluate_rule(ast_root, data):
    if ast_root.node_type == 'operand':
        return evaluate_node(ast_root, data)
    elif ast_root.node_type == 'operator':
        left_result = evaluate_rule(ast_root.left, data)
        right_result = evaluate_rule(ast_root.right, data)
        return {
            'and': left_result and right_result,
            'or': left_result or right_result
        }[ast_root.value]

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
