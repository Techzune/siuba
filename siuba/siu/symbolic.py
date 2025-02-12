from .calls import BINARY_OPS, UNARY_OPS, Call, BinaryOp, BinaryRightOp, MetaArg, UnaryOp, SliceOp, FuncArg
from .format import Formatter

# Symbolic
# =============================================================================

class Symbolic(object):
    def __init__(self, source = None, ready_to_call = False):
        self.__source = MetaArg("_") if source is None else source
        self.__ready_to_call = ready_to_call


    # allowed methods ----

    def __getattr__(self, x):
        # temporary hack working around ipython pretty.py printing
        #if x == "__class__": return Symbolic

        return Symbolic(BinaryOp(
                "__getattr__",
                self.__source,
                strip_symbolic(x)
                ))
                

    def __call__(self, *args, **kwargs) -> "Symbolic":
        if self.__ready_to_call:
            return self.__source(*args, **kwargs)

        return create_sym_call(self.__source, *args, **kwargs)

    def __getitem__(self, x):
        return Symbolic(BinaryOp(
                "__getitem__",
                self.__source,
                slice_to_call(x),
                ),
                ready_to_call = True)

    
    def __invert__(self):
        if isinstance(self.__source, Call) and self.__source.func == "__invert__":
            return self.__source.args[0]
        else: 
            return self.__op_invert()


    def __op_invert(self):
        return Symbolic(UnaryOp('__invert__', self.__source), ready_to_call = True)


    # banned methods ----

    __contains__ = None
    __iter__ = None

    def __bool__(self):
        raise TypeError("Symbolic objects can not be converted to True/False, or used "
                        "with these keywords: not, and, or.")


    # representation ----
        
    def __repr__(self):
        return Formatter().format(self.__source)


def create_sym_call(source, *args, **kwargs):
    return Symbolic(Call(
            "__call__",
            strip_symbolic(source),
            *map(strip_symbolic, args),
            **{k: strip_symbolic(v) for k,v in kwargs.items()}
            ),
            ready_to_call = True)


def slice_to_call(x):

    # TODO: uses similar code to SliceOp. make a walk_slice function?
    def f_strip(s):
        if isinstance(s, slice):
            return slice(*map(strip_symbolic, (s.start, s.stop, s.step)))

        return strip_symbolic(s)


    if isinstance(x, tuple):
        arg = tuple(map(f_strip, x))
    else:
        arg = f_strip(x)

    return SliceOp("__siu_slice__", arg)


def strip_symbolic(x):
    if isinstance(x, Symbolic):
        return x.__dict__["_Symbolic__source"]

    return x


def explain(symbol):
    """Print representation that resembles code used to create symbol."""
    if isinstance(symbol, Symbolic):
        return str(strip_symbolic(symbol))

    return str(symbol)


# Do some gnarly method setting -----------------------------------------------

def create_binary_op(op_name, left_op = True):
    def _binary_op(self, x):
        if left_op:
            node = BinaryOp(op_name, strip_symbolic(self), strip_symbolic(x))
        else:
            node = BinaryRightOp(op_name, strip_symbolic(self), strip_symbolic(x))

        return Symbolic(node, ready_to_call = True)
    return _binary_op

def create_unary_op(op_name):
    def _unary_op(self):
        node = UnaryOp(op_name, strip_symbolic(self))

        return Symbolic(node, ready_to_call = True)

    return _unary_op

for k, v in BINARY_OPS.items():
    if k in {"__getattr__", "__getitem__"}: continue
    rop = k.replace("__", "__r", 1)
    setattr(Symbolic, k, create_binary_op(k))
    setattr(Symbolic, rop, create_binary_op(rop, left_op = False))

for k, v in UNARY_OPS.items():
    if k != "__invert__":
        setattr(Symbolic, k, create_unary_op(k))


