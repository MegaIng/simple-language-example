from lark import Lark, Transformer, v_args, Token
from simple_ast import Number, InfixOperation, AST

parser = Lark(open("grammar.lark"))


class SimpleTransformer(Transformer):
    def __default__(self, data, children, meta):
        raise ValueError(data)  # This is so we see what operations we don't have implemented at the moment

    @v_args(inline=True)  # makes a bit easier to handle
    def number(self, data: Token):
        return Number(float(data))

    def infix_operator(self, children):
        """
        The function that generates the InfixOperator nodes for the
        different operators (will be used for all infix operators)
        """
        value, *rest = children  # now rest contains a list of the form [operator,operand,...]
        operators = rest[::2]  # every second one, starting at index 0, is a operator
        operands = rest[1::2]  # every second one, starting at index 1, is the operand to the operator before it
        assert len(operands) == len(operands)
        for opr, opd in zip(operators, operands):
            value = InfixOperation(opr.value, value, opd)
        return value

    mul_atom = plus_atom = power_atom = infix_operator

    @v_args(inline=True)
    def start(self, expr):  # We only have one expression at top level at the moment, so just return it
        return expr


tree = parser.parse("2*3+(5/(7-3**2))")

print(tree.pretty())

ast_tree: AST = SimpleTransformer().transform(tree)  # Transform the parse Tree to our AST representation
print(ast_tree)
print(ast_tree.execute())
