from lark import Lark

parser = Lark(open("grammar.lark"))

tree = parser.parse("2*3+(5/(7-3**2))")

print(tree.pretty())

# # Uncomment if you have pydot installed (or install it to have a nice visual overview)
# from lark.tree import pydot__tree_to_png
#
# pydot__tree_to_png(tree, "test.png")
