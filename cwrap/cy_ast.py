

#------------------------------------------------------------------------------
# Builtin types
#------------------------------------------------------------------------------

# This dict is populated by the CTypeMeta class
C_TYPES = {}


class CTypeMeta(type):

    def __new__(meta, cls_name, bases, cls_dict):
        cls = type.__new__(meta, cls_name, bases, cls_dict)
        C_TYPES[cls.c_name] = cls
        return cls


class CType(object):
    
    __metaclass__ = CTypeMeta

    c_name = ''
    
    @classmethod
    def cast(cls):
        return '<%s>' % self.c_name

    @classmethod
    def object_var_to_c(cls, name):
        return self.cast() + name

    @classmethod
    def c_var_to_object(cls, name):
        return '<object>' + name

   
class Void(CType):
    c_name = 'void'
    

class Int(CType):
    c_name = 'int'


class UInt(CType):
    c_name = 'unsigned int'


class Short(CType):
    c_name = 'short'


class UShort(CType):
    c_name = 'unsigned short'


class Char(CType):
    c_name = 'char'


class UChar(CType):
    c_name = 'unsigned char'


class Long(CType):
    c_name = 'long'


class ULong(CType):
    c_name = 'unsigned long'


class LongLong(CType):
    c_name = 'long long'


class ULongLong(CType):
    c_name = 'unsigned long long'


class Float(CType):
    c_name = 'float'


class Double(CType):
    c_name = 'double'


class LongDouble(CType):
    c_name = 'long double'


#------------------------------------------------------------------------------
# Ast nodes
#------------------------------------------------------------------------------


class ASTNode(object):

    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)
        self.location = None

    def init(self, *args, **kwargs):
        pass


class Typedef(ASTNode):

    def init(self, name, typ):
        self.name = name
        self.typ = typ


class FundamentalType(ASTNode):

    def init(self, name, size, align):
        self.name = name
        self.size = size
        self.align = align


class CvQualifiedType(ASTNode):

    def init(self, typ, const, volatile):
        self.typ = typ
        self.const = const
        self.volatile = volatile


class Ignored(ASTNode):

    def init(self, name):
        self.name = name
        self.arguments = []

    def fixup_argtypes(self, typemap):
        for arg in self.arguments:
            arg.typ = typemap[arg.typ]
            
    def add_argument(self, argument):
        self.arguments.append(argument)


class Field(ASTNode):
    
    def init(self, name, typ, bits, offset):
        self.name = name
        self.typ = typ
        self.bits = bits
        self.offset = offset
   

class Struct(ASTNode):
    
    def init(self, name, align, members, bases, size):
        self.name = name
        self.align = align
        self.members = members
        self.bases = bases
        self.size = size
    
    @property
    def opaque(self):
        return len(self.members) == 0


class Union(ASTNode):
    
    def init(self, name, align, members, bases, size):
        self.name = name
        self.align = align
        self.members = members
        self.bases = bases
        self.size = size
    
    @property
    def opaque(self):
        return len(self.members) == 0


class EnumValue(ASTNode):

    def init(self, name, value):
        self.name = name
        self.value = value


class Enumeration(ASTNode):
    
    def init(self, name, size, align):
        self.name = name
        self.size = size
        self.align = align
        self.values = []

    def add_value(self, val):
        self.values.append(val)
        
    @property
    def opaque(self):
        return len(self.values) == 1


class PointerType(ASTNode):

    def init(self, typ, size, align):
        self.typ = typ
        self.size = size
        self.align = align
        

class ArrayType(ASTNode):

    def init(self, typ, min, max):
        self.typ = typ
        self.min = int(min.rstrip('lu'))
        self.max = int(max.rstrip('lu'))


class Argument(ASTNode):

    def init(self, typ, name):
        self.typ = typ
        self.name = name


class Function(ASTNode):

    def init(self, name, returns, attributes, extern):
        self.name = name
        self.returns = returns
        self.attributes = attributes
        self.extern = extern
        self.arguments = []

    def fixup_argtypes(self, typemap):
        for arg in self.arguments:
            arg.typ = typemap[arg.typ]
            
    def add_argument(self, argument):
        self.arguments.append(argument)


class FunctionType(ASTNode):

    def init(self, returns, attributes):
        self.returns = returns
        self.attributes = attributes
        self.arguments = []

    def fixup_argtypes(self, typemap):
        for arg in self.arguments:
            arg.typ = typemap[arg.typ]
            
    def add_argument(self, argument):
        self.arguments.append(argument)


class OperatorFunction(ASTNode):

    def init(self, name, returns):
        self.name = name
        self.returns = returns


class Macro(ASTNode):

    def init(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body


class Alias(ASTNode):

    def init(self, name, value, typ=None):
        self.name = name
        self.value = value
        self.typ = typ


class File(ASTNode):

    def init(self, name):
        self.name = name
    
   
class Variable(ASTNode):

    def init(self, name, typ,  init):
        self.name = name
        self.typ = typ
        self.init = init
