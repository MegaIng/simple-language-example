from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Callable


class AST(ABC):
    """The base class of all AST-Nodes. Will contain abstract methods."""

    @abstractmethod
    def execute(self) -> float:
        """Calculates the value of this expression"""
        raise NotImplementedError

@dataclass
class Number(AST):
    """A simple constant number"""
    data: float  # For now we will simple use floats for everything

    def execute(self):
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
    """A Node with to children and one Operator to apply."""
    operator: str
    left: AST
    right: AST

    def execute(self):
        """Executes the sub expressions and applies the operators to the return values."""
        return infix_operators[self.operator](self.left.execute(), self.right.execute())


prefix_operators: Dict[str, Callable[[float], float]] = {
    '+': operator.pos,
    '-': operator.neg
}


@dataclass
class PrefixOperator(AST):
    operator: str
    operand: AST

    def execute(self):
        """Executes the sub expression and applies the operator to the value"""
        return prefix_operators[self.operator](self.operand)
