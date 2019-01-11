from __future__ import annotations

import math
import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Callable, List


class AST(ABC):
    """The base class of all AST-Nodes. Will contain abstract methods."""
    pass


class Expression(ABC):
    """The base class of all value generation AST-Nodes."""

    @abstractmethod
    def calculate(self, variables: Dict[str, float], functions: Dict[str, Callable[[float, ...], float]]):
        """
        Calculates the value of this expression, given the variables,
        which represents a mapping from variable name to current value
        and given functions, which represents a mapping from function name to callable
        """
        raise NotImplementedError


@dataclass
class Number(Expression):
    """A simple constant number"""
    data: float  # For now we will simple use floats for everything

    def calculate(self, variables: Dict[str, float], functions: Dict[str, Callable[[float, ...], float]]):
        """Simple returns the stored value"""
        return self.data


infix_operators: Dict[str, Callable[[float, float], float]] = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '**': operator.pow,
}


@dataclass
class InfixOperation(Expression):
    """Represents a infix operator application of the form '<atom> <operator> <atom>'"""
    operator: str
    left: Expression
    right: Expression

    def calculate(self, variables: Dict[str, float], functions: Dict[str, Callable[[float, ...], float]]):
        """Executes the sub expressions and applies the operators to the return values."""
        return infix_operators[self.operator](self.left.calculate(variables, functions),
                                              self.right.calculate(variables, functions))


prefix_operators: Dict[str, Callable[[float], float]] = {
    '+': operator.pos,
    '-': operator.neg
}


@dataclass
class PrefixOperator(Expression):
    """Represents a prefix operator application of the 'form <operator> <atom>'"""
    operator: str
    operand: Expression

    def calculate(self, variables: Dict[str, float], functions: Dict[str, Callable[[float, ...], float]]):
        """Executes the sub expression and applies the operator to the value"""
        return prefix_operators[self.operator](self.operand.calculate(variables, functions))


builtin_functions: Dict[str, Callable[[float, ...], float]] = {
    'cos': math.cos,
    'sin': math.sin,
    'tan': math.tan,
    'abs': operator.abs,
    'rad': math.radians,
    'deg': math.degrees,
    'acos': math.acos,
    'asin': math.asin,
    'atan': math.atan,
    'atan2': math.atan2,
    'max': max,
    'min': min,
}


@dataclass
class FunctionCall(Expression):
    """Represents a function application of the form <function_name>(<atom>,...)"""
    name: str
    arguments: List[Expression]

    def calculate(self, variables: Dict[str, float], functions: Dict[str, Callable[[float, ...], float]]):
        """
        Executes all arguments and calls the function, returning its result.
        The function name is first looked up in `functions`, then in `builtin_functions`
        """
        if self.name in functions:
            return functions[self.name](*(a.calculate(variables, functions) for a in self.arguments))
        elif self.name in builtin_functions:
            return builtin_functions[self.name](*(a.calculate(variables, functions) for a in self.arguments))
        else:
            raise ValueError(self.name)


builtin_constants: Dict[str, float] = {
    'pi': math.pi,
    'e': math.e,
}


@dataclass
class Variable(Expression):
    """Represents a variable loading? lookup? whatever you want to call it"""
    name: str

    def calculate(self, variables: Dict[str, float], functions: Dict[str, Callable[[float, ...], float]]):
        if self.name in variables:
            return variables[self.name]
        elif self.name in builtin_constants:
            return builtin_constants[self.name]
        else:
            raise ValueError(self.name)


class Statement(AST, ABC):
    """The base class of all executable AST-Nodes (having side effects, especially definitions)"""

    @abstractmethod
    def execute(self, variables: Dict[str, float], functions: Dict[str, Callable[[float, ...], float]]):
        raise NotImplementedError


@dataclass
class VariableDefinition(Statement):
    """Represents a variable assignment"""
    name: str
    value: Expression

    def execute(self, variables: Dict[str, float], functions: Dict[str, Callable[[float, ...], float]]):
        """
        Executes value with the given variables and functions, and then
        stores it under `name` overwriting anything that was there before
        """
        variables[self.name] = self.value.calculate(variables, functions)


@dataclass
class FunctionDefinition(Statement):
    """Represents a function assignment"""
    name: str
    parameters: List[str]
    expr: Expression

    def execute(self, variables: Dict[str, float], functions: Dict[str, Callable[[float, ...], float]]):
        """
        Creates a `_Function` object, given the current `variables` and `functions`, and then
        stores it under `name` overwriting anything that was there before
        """
        functions[self.name] = _Function(variables, functions, self.parameters, self.expr)


@dataclass
class _Function:
    """Internal class used by the `FunctionDefinition` Node to create
     very basic 'closures', meaning that the expression can access defined functions and variables"""
    outer_variables: Dict[str, float]
    outer_functions: Dict[str, Callable[[float, ...], float]]
    parameters: List[str]
    expr: Expression

    def __call__(self, *args: float) -> float:
        assert len(self.parameters) == len(args)
        vars = {**self.outer_variables, **dict(zip(self.parameters, args))}
        return self.expr.calculate(vars, self.outer_functions)
