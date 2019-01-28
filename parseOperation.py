#!/usr/bin/python3
# # -*- coding: utf-8 -*-

import ast
import operator as op
import logging

class parse_operation:
    def __init__(self):
        self.logger = logging.getLogger()
        self.operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

    def __eval_expr(self, expr):
        """
        >>> eval_expr('2^6')
        4
        >>> eval_expr('2**6')
        64
        >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
        -5.0
        """
        return self.__eval(ast.parse(expr, mode='eval').body)

    def __eval(self, node):
        if isinstance(node, ast.Num): # <number>
            return node.n
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return self.operators[type(node.op)](self.__eval(node.left), self.__eval(node.right))
        elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
            return self.operators[type(node.op)](self.__eval(node.operand))
        else:
            raise TypeError(node)

    def parse(self, operation):
        result = self.__eval_expr(operation)
        self.logger.debug("%s = %s", operation, str(result))
        return result
