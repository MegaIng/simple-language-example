from lark import Lark, Transformer, v_args, Token
from simple_ast import Number, InfixOperation, AST, FunctionCall, Variable, FunctionDefinition, VariableDefinition

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

    def start(self, children):
        *statements, expr = children
        return statements, expr

    @v_args(inline=True)
    def function_call(self, name: Token, *args):
        return FunctionCall(name.value, list(args))

    @v_args(inline=True)
    def variable(self, name: Token):
        return Variable(name.value)

    def function_definition(self, children):
        name, *parms, expr = children
        return FunctionDefinition(name.value, list(parms), expr)

    @v_args(inline=True)
    def variable_definition(self, name: Token, expr: AST):
        return VariableDefinition(name.value, expr)


tree = parser.parse("""
a := 6
f(b) := a + 4
a := 7

f(5)
""")

print(tree.pretty())

statements, expr = SimpleTransformer().transform(tree)
vars, funcs = {}, {}
for st in statements:
    st.execute(vars, funcs)
print(expr.calculate(vars, funcs))
