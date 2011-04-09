from collections import defaultdict


class ASTNode(object):

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.init(*args, **kwargs)

    def init(self, *args, **kwargs):
        pass

    def render(self):
        raise NotImplementedError
    
    @property
    def module(self):
        """ Grab the top level module node from any given node.

        """
        if isinstance(self, Module):
            return self
        else:
            return self.parent.module


#------------------------------------------------------------------------------
# Fundamental Types
#------------------------------------------------------------------------------
class FundamentalType(ASTNode):
    
    _c_type = ''

    def c_var_to_object(self, name):
        return name

    def object_var_to_c(self, name):
        return name

    def c_type(self):
        return self._c_type


class Void(FundamentalType):
    _c_type = 'void'


class Int(FundamentalType):
    _c_type = 'int'


class UInt(FundamentalType):
    _c_type = 'unsigned int'


class Short(FundamentalType):
    _c_type = 'short'


class UShort(FundamentalType):
    _c_type = 'unsigned int'


class Char(FundamentalType):
    _c_type = 'char'


class UChar(FundamentalType):
    _c_type = 'unsigned char'


class Long(FundamentalType):
    _c_type = 'long'


class ULong(FundamentalType):
    _c_type = 'unsigned long'


class LLong(FundamentalType):
    _c_type = 'long long'


class ULLong(FundamentalType):
    _c_type = 'unsigned long long'


class Float(FundamentalType):
    _c_type = 'float'


class Double(FundamentalType):
    _c_type = 'double'


class LDouble(FundamentalType):
    _c_type = 'long double'


fundamental_map = {
    ('char',): Char,
    ('char', 'signed'): Char,
    ('char', 'unsigned'): UChar,
    ('double',): Double,
    ('double', 'long'): LDouble,
    ('float',): Float,
    ('int',): Int, 
    ('int', 'long'): Long,
    ('int', 'long', 'long'): LLong,
    ('int', 'long', 'signed'): Long,
    ('int', 'long', 'unsigned'): ULong,
    ('int', 'long', 'long', 'signed'): LLong,
    ('int', 'long', 'long', 'unsigned'): ULLong,
    ('int', 'short'): Short, 
    ('int', 'short', 'signed'): Short,
    ('int', 'short', 'unsigned'): UShort,
    ('int', 'signed'): Int,
    ('int', 'unsigned'): UInt,
    ('long',): Long,
    ('long', 'long'): LLong,
    ('long', 'signed'): Long,
    ('long', 'unsigned'): ULong,
    ('long', 'long', 'signed'): LLong,
    ('long', 'long', 'unsigned'): ULLong,
    ('short',): Short,
    ('short', 'unsigned'): UShort,
    ('short', 'signed'): Short,
    ('void',): Void,
}


def gen_type(type_name):
    class DummyType(FundamentalType):
        _c_type = type_name
    return DummyType


def get_fundamental_type(*names):
    key = tuple(sorted(names))
    if key not in fundamental_map:
        #raise TypeError('Cannot find fundamental type for `%s`' % names)
        res = gen_type(key[0])
    else:
        res = fundamental_map[key]
    return res


#------------------------------------------------------------------------------
# Structs, Unions, Enums
#------------------------------------------------------------------------------
class Field(ASTNode):
    
    def init(self, identifier=None, typ=None):
        self.identifier = identifier
        self.typ = typ
        self.mode = 'rw'

class Container(ASTNode):
    
    def init(self, identifier=None, fields=None):
        self.identifier = identifier
        self.fields = fields or []
    
    def add_field(self, field):
        self.fields.append(field)


class Struct(Container):
    pass


class Union(Container):
    pass


class EnumValue(ASTNode):

    def init(self, identifier=None, value=None):
        self.identifier = identifier
        self.value = value


class Enum(ASTNode):

    def init(self, identifier=None, values=None):
        self.identifier = identifier
        self.values = values or []

    def add_value(self, value):
        self.values.append(value)
    

#------------------------------------------------------------------------------
# Pointers and Arrays
#------------------------------------------------------------------------------
class Pointer(ASTNode):

    def init(self, typ=None):
        self.typ = typ


class Array(ASTNode):

    def init(self, typ=None, dim=None):
        self.typ = typ
        self.dim = dim


#------------------------------------------------------------------------------
# Typedef
#------------------------------------------------------------------------------
class Typedef(ASTNode):

    def init(self, identifier=None, typ=None):
        self.identifier = identifier
        self.typ = typ


#------------------------------------------------------------------------------
# Function
#------------------------------------------------------------------------------
class Argument(ASTNode):

    def init(self, identifier=None, typ=None):
        self.identifier = identifier
        self.typ = typ


class Function(ASTNode):

    def init(self, identifier=None, res_typ=None, arguments=None):
        self.identifier = identifier
        self.res_typ = res_typ
        self.arguments = arguments or []

    def add_argument(self, argument):
        self.arguments.append(argument)


#------------------------------------------------------------------------------
# Module
#------------------------------------------------------------------------------
class Module(ASTNode):

    def init(self, items=None):
        self.items = items or []
    
    def add_item(self, item):
        self.items.append(item)
    
   
