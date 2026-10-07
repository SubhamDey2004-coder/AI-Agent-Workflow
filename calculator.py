import ast
import operator


operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg
}


def calculate(expression):

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):

        if isinstance(node, ast.Constant):

            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("Only numbers are allowed.")

        if isinstance(node, ast.BinOp):

            left = evaluate(node.left)
            right = evaluate(node.right)

            operation = operators.get(type(node.op))

            if operation is None:
                raise ValueError("Operator not allowed.")

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):

            value = evaluate(node.operand)

            operation = operators.get(type(node.op))

            if operation is None:
                raise ValueError("Operator not allowed.")

            return operation(value)

        raise ValueError("Invalid expression.")

    return evaluate(tree.body)