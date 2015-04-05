import ast
import inspect

from ast import (
    copy_location,

    Assign, Load, Name, Store, Tuple, While
)
from functools import wraps


def deindent(source):
    if source.startswith(" "):
        lines = source.split("\n")
        level = len(filter(lambda s: not s, lines[0].split(" ")))
        return "\n".join(line[level:] for line in lines)

    return source


def isa(n, k):
    return isa_and_has(n, k)


def isa_and_has(n, k, **kwargs):
    if not isinstance(n, k):
        return False

    for key, value in kwargs.items():
        if getattr(n, key) != value:
            return False

    return True


class TCOTransformer(ast.NodeTransformer):
    def __init__(self, name):
        self.name = name
        self.args = None

    def visit_Return(self, node):
        if isa(node.value, ast.Call):
            call = node.value
            if isa_and_has(call.func, Name, id=self.name):
                value = Tuple(call.args, Load())
                targets = Tuple([], Store())
                for i, argument in enumerate(self.args.args):
                    targets.elts.append(Name(argument.id, ast.Store()))

                return copy_location(Assign([targets], value), node)

        if isinstance(node.value, Name):
            return node

        raise TypeError("invalid expression in tail position")

    def visit_FunctionDef(self, node):
        self.args = node.args

        decorators, body = [], []
        for child in node.decorator_list:
            if isinstance(child, Name) and child.id == "tco":
                continue

            decorators.append(child)

        for child in node.body:
            body.append(self.visit(child))

        while_block = While(ast.Num(1), [], [])
        while_block.body = body
        node.decorator_list = decorators
        node.body = [while_block]
        return node


def tco(f):
    name = f.__name__
    filename = inspect.getsourcefile(f)
    source = inspect.getsource(f)
    module = inspect.getmodule(f)
    tree = ast.parse(deindent(source))
    tree = TCOTransformer(name).visit(tree)
    tree = ast.fix_missing_locations(tree)
    code = compile(tree, filename, "exec")
    globals_, locals_ = module.__dict__, {}
    for i, var_name in enumerate(f.__code__.co_freevars):
        if var_name == name:
            continue

        globals_[var_name] = f.__closure__[i].cell_contents

    exec code in globals_, locals_
    return wraps(f)(locals_[name])
