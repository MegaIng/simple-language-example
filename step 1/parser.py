from lark import Lark

parser = Lark(open("grammar.lark"))  # Load grammar. You can also hardcode the grammar into the sourcecode

tree = parser.parse("2*3+(5/(7-3**2))")  # Let lark parse and create a tree

print(tree.pretty())  # Print the tree with a bit of indentation

# # Uncomment if you have pydot installed (or install it to have a nice visual overview)
# from lark.tree import pydot__tree_to_png
#
# pydot__tree_to_png(tree, "test.png")
