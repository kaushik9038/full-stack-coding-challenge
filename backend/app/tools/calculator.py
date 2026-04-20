"""A tiny calculator tool.

It only supports simple expressions like:
calculate 2 + 2
what is 5 * 8
"""

import ast
import operator
import re


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def looks_like_math(lower_task: str) -> bool:
    has_math_word = any(word in lower_task for word in ["calculate", "math", "add", "subtract", "multiply", "divide"])
    has_math_symbols = re.search(r"-?\d+(\.\d+)?\s*[\+\-\*\/]\s*-?\d+(\.\d+)?", lower_task)
    return has_math_word or bool(has_math_symbols)


def calculate_answer(task_text: str) -> str:
    expression = find_expression(task_text)
    result = evaluate_expression(expression)
    return str(result)


def find_expression(task_text: str) -> str:
    match = re.search(r"(-?\d+(?:\.\d+)?(?:\s*[\+\-\*\/]\s*-?\d+(?:\.\d+)?)+)", task_text)
    if not match:
        raise ValueError("I found a calculator task, but not a clear expression like 2 + 2.")
    return match.group(1)


def evaluate_expression(expression: str):
    try:
        tree = ast.parse(expression, mode="eval")
        answer = evaluate_node(tree.body)
    except ZeroDivisionError as error:
        raise ValueError("Division by zero is not supported.") from error

    if isinstance(answer, float) and answer.is_integer():
        return int(answer)
    return answer


def evaluate_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = evaluate_node(node.left)
        right = evaluate_node(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        value = evaluate_node(node.operand)
        return ALLOWED_OPERATORS[type(node.op)](value)

    raise ValueError("Only simple arithmetic is supported.")
