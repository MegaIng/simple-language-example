import math

from lark import Lark, Transformer, v_args, Token
from simple_ast import Number, InfixOperation, AST, FunctionCall, Variable

parser = Lark(open("grammar.lark"))


class SimpleTransformer(Transformer):
    def __default__(self, data, children, meta):
        raise ValueError(data)

    @v_args(inline=True)
    def number(self, data: Token):
        return Number(float(data))

    def infix_operator(self, children):
        """
        The function that generates the InfixOperator nodes for the
        different operators (will be used for all infix operators)
        """
        value, *rest = children
        operators = rest[::2]
        operands = rest[1::2]
        assert len(operands) == len(operands)
        for opr, opd in zip(operators, operands):
            value = InfixOperation(opr.value, value, opd)
        return value

    mul_atom = plus_atom = power_atom = infix_operator

    @v_args(inline=True)
    def start(self, expr):
        return expr

    @v_args(inline=True)
    def function_call(self, name: Token, *args):
        return FunctionCall(name.value, args)

    @v_args(inline=True)
    def variable(self, name: Token):
        return Variable(name.value)


tree = parser.parse("cos(pi)")

print(tree.pretty())

ast_tree: AST = SimpleTransformer().transform(tree)
print(ast_tree)
print(ast_tree.execute({'pi': math.pi}))
