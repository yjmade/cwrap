

class ASTNode(object):

    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)
        self.location = None

    def init(self, *args, **kwargs):
        pass
    
    def refs(self):
        return []


class Typedef(ASTNode):

    def init(self, name, typ, context):
        self.name = name
        self.typ = typ
        self.context = context
        self.spoofed = False
        
    def refs(self):
        return [self.typ]
    

class FundamentalType(ASTNode):

    def init(self, name, size, align):
        self.name = name
        self.size = size
        self.align = align

    def refs(self):
        return []


class CvQualifiedType(ASTNode):

    def init(self, typ, const, volatile):
        self.typ = typ
        self.const = const
        self.volatile = volatile

    def refs(self):
        return [self.typ]


class Ignored(ASTNode):

    def init(self, name):
        self.name = name
        self.arguments = []

    def fixup_argtypes(self, typemap):
        for arg in self.arguments:
            arg.typ = typemap[arg.typ]
            
    def add_argument(self, argument):
        self.arguments.append(argument)

    def refs(self):
        return self.arguments


class Field(ASTNode):
    
    def init(self, name, typ, context, bits, offset):
        self.name = name
        self.typ = typ
        self.context = context
        self.bits = bits
        self.offset = offset
   
    def refs(self):
        return [self.typ]


class Struct(ASTNode):
    
    def init(self, name, align, members, context, bases, size):
        self.name = name
        self.align = align
        self.members = members
        self.context = context
        self.bases = bases
        self.size = size
        self.spoofed = False

    @property
    def opaque(self):
        return len(self.members) == 0

    def refs(self):
        return self.members


class Union(ASTNode):
    
    def init(self, name, align, members, context, bases, size):
        self.name = name
        self.align = align
        self.members = members
        self.context = context
        self.bases = bases
        self.size = size
        self.spoofed = False

    @property
    def opaque(self):
        return len(self.members) == 0

    def refs(self):
        return self.members


class EnumValue(ASTNode):

    def init(self, name, value):
        self.name = name
        self.value = value
    
    def refs(self):
        return []


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
    
    def refs(self):
        return self.values


class PointerType(ASTNode):

    def init(self, typ, size, align):
        self.typ = typ
        self.size = size
        self.align = align
    
    def refs(self):
        return [self.typ]


class ArrayType(ASTNode):

    def init(self, typ, min, max):
        self.typ = typ
        self.min = min
        self.max = max
    
    def refs(self):
        return [self.typ]


class Argument(ASTNode):

    def init(self, typ, name):
        self.typ = typ
        self.name = name

    def refs(self):
        return [self.typ]


class Function(ASTNode):

    def init(self, name, returns, context, attributes, extern):
        self.name = name
        self.returns = returns
        self.context = context
        self.attributes = attributes
        self.extern = extern
        self.arguments = []

    def fixup_argtypes(self, typemap):
        for arg in self.arguments:
            arg.typ = typemap[arg.typ]
            
    def add_argument(self, argument):
        self.arguments.append(argument)

    def refs(self):
        return [self.returns] + self.arguments


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
    
    def refs(self):
        return [self.returns] + self.arguments


class OperatorFunction(ASTNode):

    def init(self, name, returns):
        self.name = name
        self.returns = returns

    def refs(self):
        return [self.returns]


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
    
    def refs(self):
        return [self.typ]


class File(ASTNode):

    def init(self, name):
        self.name = name
    
  
class Namespace(ASTNode):

    def init(self, name, members):
        self.name = name
        self.members = members

    def refs(self):
        return self.members
    

class Variable(ASTNode):

    def init(self, name, typ, context, init):
        self.name = name
        self.typ = typ
        self.context = context
        self.init = init

    def refs(self):
        return [self.typ]


