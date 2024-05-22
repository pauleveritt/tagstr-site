import dis  # useful for showing the scope analysis
from types import FunctionType

from tagstr_site.tagtyping import Decoded, Interpolation
from tagstr_site.taglib import decode_raw


def param_list(names):
    return ', '.join(names)


def name_bindings(names, /, indent):
    code_text = ['{']
    for name in names:
        code_text.append(f'    {name!r} : {name},')
    code_text.append('}')
    return f'\n{" " * indent}'.join(code_text)


def rewrite_interpolation(interpolation: Interpolation) -> Interpolation:
    """Given an interpolation, return a rewritten interpolation to return any used names.
    
    When the interpolation's getvalue is evaluated, returns a dict of name to any bound
    value.
    """
    getvalue, raw, conv, formatspec = interpolation
    code = getvalue.__code__
    print(f'Compiling interpolation {hash(getvalue.__code__)}')
    dis.dis(code)
    all_names = code.co_names + code.co_freevars

    # # Implement the "lambda trick"
    wrapped = f"""
def outer({param_list(code.co_freevars)}):
    def inner():
        return {name_bindings(all_names, indent=8)}
"""
    print(wrapped)

    capture = {}
    exec(wrapped, getvalue.__globals__, capture)
    new_lambda_code = capture["outer"].__code__.co_consts[1]
    dis.dis(new_lambda_code)

    new_getvalue = FunctionType(
        new_lambda_code,
        getvalue.__globals__,
        getvalue.__name__,
        getvalue.__defaults__, 
        getvalue.__closure__)

    return new_getvalue, wrapped, conv, formatspec


def rewritten(*args: Decoded | Interpolation):
    new_args = []
    for arg in decode_raw(*args):
        match arg:
            case str():
                new_args.append(arg)
            case _:
                new_args.append(rewrite_interpolation(arg))
    return new_args


# Set up some variables at differing level of nested scope
a = 2
def nested1():
    b = 3
    def nested2():
        c = 5
        def nested3():
            d = 7
            # new_args is rewritten such that each interpolation's getvalue is a new
            # function/code object that returns that the mapping of the
            # variables that are used to their values (namely, for a, b, c, d)
            new_args = rewritten"{d**a + c * c * c * a * b * a + d}"
            print(new_args[0][0]())
        nested3()
    nested2()
nested1()
