class C_ASTNode(object):

    def __init__(self, *args, **kwargs):
        self.location = None
        #self.render_hints = {}
        self.name = ''
        self.init(*args, **kwargs)
       
    def init(self, *args, **kwargs):
        pass
  
    
class Typedef(C_ASTNode):

    def init(self, name, typ, context):
        self.name = name
        self.typ = typ
        self.context = context


class FundamentalType(C_ASTNode):

    def init(self, name): #, size, align):
        self.name = name
        #self.size = size
        #self.align = align


class CvQualifiedType(C_ASTNode):

    def init(self, typ, const, volatile):
        self.typ = typ
        self.const = const
        self.volatile = volatile


class Ignored(C_ASTNode):

    def init(self, name):
        self.name = name
        self.arguments = []

    def fixup_argtypes(self, typemap):
        for arg in self.arguments:
            arg.typ = typemap[arg.typ]
            
    def add_argument(self, argument):
        if argument is not None:
            self.arguments.append(argument)

    add_child = add_argument


class Field(C_ASTNode):
    
    def init(self, name, typ, context, bits=None, offset=None):
        self.name = name
        self.typ = typ
        self.context = context
        #self.bits = bits
        #self.offset = offset
   

class Struct(C_ASTNode):
    
    def init(self, name, members = None, context = None):
        self.name = name
        self.members = members if members is not None else []
        self.context = context

    @property
    def opaque(self):
        return len(self.members) == 0

    def add_member(self, member):
        if member is not None:
            self.members.append(member)

    add_child = add_member


class Union(C_ASTNode):
    
    def init(self, name, align = None, members = [], context = None, bases = None, size = None):
        self.name = name
        #self.align = align
        self.members = members
        self.context = context
        #self.bases = bases
        #self.size = size

    @property
    def opaque(self):
        return len(self.members) == 0

    def add_member(self, member):
        if member is not None:
            self.members.append(member)

    add_child = add_member
            
class EnumValue(C_ASTNode):

    def init(self, name, value):
        self.name = name
        self.value = value
    

class Enumeration(C_ASTNode):
    
    def init(self, name, context):
        self.name = name
        self.context = context
        self.values = []

    def add_value(self, val):
        self.values.append(val)

    add_child = add_value
        
    @property
    def opaque(self):
        return len(self.values) == 1
    

class PointerType(C_ASTNode):

    def init(self, typ, size, align):
        self.typ = typ
        self.size = size
        self.align = align
    
    @property
    def refs(self):
        return [self.typ]


class ArrayType(C_ASTNode):

    def init(self, typ, min, max):
        self.typ = typ
        self.min = min
        self.max = max
    

class Argument(C_ASTNode):

    def init(self, name, typ):
        self.typ = typ
        self.name = name


class Function(C_ASTNode):

    def init(self, name, returns, context=None, attributes=None, extern=None):
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
        if argument is not None:
            self.arguments.append(argument)

    add_child = add_argument

class FunctionType(C_ASTNode):

    def init(self, returns, attributes):
        self.returns = returns
        self.attributes = attributes
        self.arguments = []

    def fixup_argtypes(self, typemap):
        for arg in self.arguments:
            arg.typ = typemap[arg.typ]
            
    def add_argument(self, argument):
        self.arguments.append(argument)
    
    add_child = add_argument

class OperatorFunction(C_ASTNode):

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
        if argument is not None:
            self.arguments.append(argument)

    add_child = add_argument

class Macro(C_ASTNode):

    def init(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body


class Alias(C_ASTNode):

    def init(self, name, value, typ=None):
        self.name = name
        self.value = value
        self.typ = typ
    

class File(C_ASTNode):

    def init(self, name, members = None):
        self.name = name
        self.members = members if members is not None else []

    def add_member(self, member):
        if member is not None:
            self.members.append(member)

    add_child = add_member
        
        

class Namespace(C_ASTNode):

    def init(self, name, members = None):
        self.name = name
        self.members = members if members is not None else []
        
    def add_member(self, member):
        if member is not None:
            self.members.append(member)
    
    add_child = add_member


class Variable(C_ASTNode):

    def init(self, name, typ, context, init):
        self.name = name
        self.typ = typ
        self.context = context
        self.init = init

#-----------------
# C++ nodes
#-----------------

class Class(C_ASTNode):
    
    def init(self, name, members = None, context = None):
        self.name = name
        self.members = members if members is not None else []
        self.context = context

    def add_member(self, member):
        if member is not None:
            self.members.append(member)

    add_child = add_member
