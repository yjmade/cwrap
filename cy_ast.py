

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

class Location(object):

    def __init__(self, header, lineno):
        self.header = header
        self.lineno = lineno


class ASTNode(object):

    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)

    def init(self, *args, **kwargs):
        pass


#------------------------------------------------------------------------------
# Typedef
#------------------------------------------------------------------------------
class Typedef(ASTNode):

    def init(self, identifier, location=None):
        self.identifier = identifier
        self.location = location
        self._typ = None

    @property
    def typ(self):
        return self._typ
    
    @typ.setter
    def typ(self, val):
        if self._typ is not None:
            raise RuntimeError('Typedef type already set.')
        self._typ = val


#------------------------------------------------------------------------------
# Structs, Unions, Enums
#------------------------------------------------------------------------------
class Field(ASTNode):
    
    def init(self, identifier, location=None):
        self.identifier = identifier
        self.location = location
        self.typ = None
     

class EnumValue(ASTNode):

    def init(self, identifier, value):
        self.identifier = identifier
        self.value = value

   
class Container(ASTNode):
    
    def init(self, identifier, location=None):
        self.identifier = identifier
        self.location = location
        self.fields = []
    
    def add_field(self, field):
        self.fields.append(field)
    
    @property
    def opaque(self):
        return len(self.fields) == 0


class Struct(Container):
    pass


class Union(Container):
    pass


class Enum(Container):
    pass
        

#------------------------------------------------------------------------------
# Pointers and Arrays
#------------------------------------------------------------------------------
class Pointer(ASTNode):

    def init(self):
        self.typ = None


class Array(ASTNode):

    def init(self, dim):
        self.typ = None
        self.dim = dim



#------------------------------------------------------------------------------
# Function
#------------------------------------------------------------------------------
class Argument(ASTNode):

    def init(self, identifier):
        self.identifier = identifier
        self.typ = None


class Function(ASTNode):

    def init(self, identifier, location):
        self.identifier = identifier
        self.location = location
        self.res_typ = None
        self.arguments = []

    def add_argument(self, argument):
        self.arguments.append(argument)


#------------------------------------------------------------------------------
# Module
#------------------------------------------------------------------------------
class Module(ASTNode):

    def init(self):
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)
    
   
