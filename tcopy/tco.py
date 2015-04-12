import ast
import inspect

from ast import (
    Assign, Call, Continue, Load, Name, Num, Store, Tuple, While
)
from functools import wraps


def deindent(source):
    if source.startswith(" "):
        lines = source.split("\n")
        level = len(filter(lambda s: not s, lines[0].split(" ")))
        return "\n".join(line[level:] for line in lines)

    return source


def isa(n, k, **kwargs):
    if not isinstance(n, k):
        return False

    for key, value in kwargs.items():
        if getattr(n, key) != value:
            return False

    return True


def build_error(source, node, message):
    lines = source.split("\n")
    lines = "\n".join(lines[node.lineno - 3:node.lineno])
    caret = "~" * node.col_offset + "^"
    return "{message}:\n{lines}\n{caret}".format(
        message=message, lines=lines, caret=caret
    )


class TailValidator(ast.NodeVisitor):
    def __init__(self, name, source):
        self.name = name
        self.source = source

    def visit_Call(self, node):
        if isa(node.func, Name, id=self.name):
            raise TypeError(build_error(
                self.source, node, "invalid expression in tail position"
            ))

        self.generic_visit(node)


class TCOTransformer(ast.NodeTransformer):
    def __init__(self, name, source):
        self.name = name
        self.source = source
        self.validator = TailValidator(name, source)
        self.args = None
        self.found_term = False

    def visit_Return(self, node):
        if isa(node.value, Call):
            call = node.value
            if isa(call.func, Name, id=self.name):
                indices = {}
                value_list = [None] * len(self.args.args)
                value = Tuple(value_list, Load())
                target = Tuple([], Store())
                for i, argument in enumerate(self.args.args):
                    indices[argument.id] = i
                    target.elts.append(Name(argument.id, Store()))

                for i, argument in enumerate(call.args):
                    value_list[i] = argument

                for keyword in call.keywords:
                    i = indices[keyword.arg]
                    value_list[i] = keyword.value

                if any(map(lambda x: x is None, value_list)):
                    raise TypeError(build_error(
                        self.source, call, "bad arity in tail-positioned expression"
                    ))

                assignment = Assign([target], value)
                continue_ = Continue()
                return [assignment, continue_]

        self.validator.visit(node.value)
        self.found_term = True
        return node

    def visit_FunctionDef(self, node):
        self.args = node.args

        decorators, body = [], []
        for child in node.decorator_list:
            if isa(child, Name, id="tco"):
                continue

            decorators.append(child)

        for child in node.body:
            child = self.visit(child)
            if isa(child, list):
                body.extend(child)
            else:
                body.append(child)

        if not self.found_term:
            raise TypeError("no terminating case")

        # Drop final `continue` from while block.
        if isa(body[-1], Continue):
            body = body[:-1]

        node.decorator_list = decorators
        node.body = [While(Num(1), body, [])]
        return node


def tco(f):
    name = f.__name__
    filename = inspect.getsourcefile(f)
    source = inspect.getsource(f)
    tree = ast.parse(deindent(source))
    tree = TCOTransformer(name, source).visit(tree)
    tree = ast.fix_missing_locations(tree)
    code = compile(tree, filename, "exec")
    globals_, locals_ = dict(f.__globals__), {}
    deferred = {}
    for i, var_name in enumerate(f.__code__.co_freevars):
        if var_name == name:
            continue

        try:
            globals_[var_name] = f.__closure__[i].cell_contents
        except ValueError:
            deferred[var_name] = f.__closure__[i]

    exec code in globals_, locals_
    func = wraps(f)(locals_[name])

    if deferred:
        def wrapper(*args, **kwargs):
            for var_name, cell in deferred.items():
                globals_[var_name] = cell.cell_contents
                del deferred[var_name]

            return func(*args, **kwargs)

        return wrapper

    return func
