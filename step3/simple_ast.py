from __future__ import annotations

import math
import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Callable, List


class AST(ABC):
    """The base class of all AST-Nodes. Will contain abstract methods."""

    @abstractmethod
    def execute(self, context: Dict[str, float]) -> float:
        """
        Calculates the value of this expression, given the context,
        which represents a mapping from variable name to current value
        """
        raise NotImplementedError


@dataclass
class Number(AST):
    """A simple constant number"""
    data: float  # For now we will simple use floats for everything

    def execute(self, context: Dict[str, float]) -> float:
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
class InfixOperation(AST):
    """Represents a infix operator application of the form '<atom> <operator> <atom>'"""
    operator: str
    left: AST
    right: AST

    def execute(self, context: Dict[str, float]) -> float:
        """Executes the sub expressions and applies the operators to the return values."""
        return infix_operators[self.operator](self.left.execute(context), self.right.execute(context))


prefix_operators: Dict[str, Callable[[float], float]] = {
    '+': operator.pos,
    '-': operator.neg
}


@dataclass
class PrefixOperator(AST):
    """Represents a prefix operator application of the 'form <operator> <atom>'"""
    operator: str
    operand: AST

    def execute(self, context: Dict[str, float]) -> float:
        """Executes the sub expression and applies the operator to the value"""
        return prefix_operators[self.operator](self.operand)


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
class FunctionCall(AST):
    """Represents a function application of the form <function_name>(<atom>,...)"""
    name: str
    arguments: List[AST]

    def execute(self, context: Dict[str, float]) -> float:
        """Executes all arguments and calls the function, returning its result"""
        return builtin_functions[self.name](*(a.execute(context) for a in self.arguments))


@dataclass
class Variable(AST):
    """Represents a variable loading? lookup? whatever you want to call it"""
    name: str

    def execute(self, context: Dict[str, float]):
        return context[self.name]
