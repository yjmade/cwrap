from pycparser import c_ast as pcp_ast
import cy_ast


class ASTTranslator(object):
    """ Translates a PyCParser AST into a Cython code 
    generation AST.

    """
    def __init__(self):
        self.parents = [None]

    def visit(self, node):
        """ The main entry point. Call this method with a node
        from a pycparser AST. The return value will be 
        a corresponding Cython code generation AST.

        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        print 'unhandled node', type(node)

    def visit_FileAST(self, node):
        return self.generate_module(node)

    def visit_Typedef(self, node):
        return self.generate_typedef(node)

    def visit_Struct(self, node):
        return self.generate_struct(node)
   
    def visit_Decl(self, node):
        if isinstance(node.type, (pcp_ast.Struct, pcp_ast.Union, pcp_ast.Enum,
                                  pcp_ast.FuncDecl)):
            return self.visit(node.type)
        else:
            print 'unhandled toplevel decl type', node.type

    def visit_TypeDecl(self, node):
        return self.visit(node.type)

    def visit_IdentifierType(self, node):
        return self.generate_fundamental_type(node)
    
    def visit_PtrDecl(self, node):
        return self.generate_pointer(node)
    
    def visit_ArrayDecl(self, node):
        return self.generate_array(node)
    
    def visit_Enum(self, node):
        return self.generate_enum(node)

    def visit_Enumerator(self, node):
        return self.generate_enum_value(node)
    
    def visit_Union(self, node):
        return self.generate_union(node)

    def visit_FuncDecl(self, node):
        return self.generate_func(node)

    def generate_typedef(self, typedef_node):
        parent = self.parents[-1]
        identifier = typedef_node.name
        typedef = cy_ast.Typedef(parent, identifier)
        self.parents.append(typedef)
        typedef.typ = self.visit(typedef_node.type)
        self.parents.pop()
        return typedef

    def generate_struct(self, struct_node):
        parent = self.parents[-1]
        identifier = struct_node.name
        struct = cy_ast.Struct(parent, identifier)
        self.parents.append(struct)
        if struct_node.decls:
            for decl in struct_node.decls:
                struct.add_field(self.generate_field(decl))
        self.parents.pop()
        return struct

    def generate_field(self, decl_node):
        parent = self.parents[-1]
        identifier = decl_node.name
        field = cy_ast.Field(parent, identifier)
        self.parents.append(field)
        field.typ = self.visit(decl_node.type)
        self.parents.pop()
        return field

    def generate_fundamental_type(self, type_node):
        parent = self.parents[-1]
        names = type_node.names
        typ = cy_ast.get_fundamental_type(*names)
        return typ(parent)

    def generate_pointer(self, ptr_node):
        parent = self.parents[-1]
        pointer = cy_ast.Pointer(parent)
        self.parents.append(pointer)
        pointer.typ = self.visit(ptr_node.type)
        self.parents.pop()
        return pointer

    def generate_array(self, array_node):
        parent = self.parents[-1]
        array = cy_ast.Array(parent, int(array_node.dim.value))
        self.parents.append(array)
        array.typ = self.visit(array_node.type)
        self.parents.pop()
        return array

    def generate_enum(self, enum_node):
        parent = self.parents[-1]
        identifier = enum_node.name
        enum = cy_ast.Enum(parent, identifier)
        self.parents.append(enum)
        for value in enum_node.values.enumerators:
            enum.add_value(self.visit(value))
        self.parents.pop()
        return enum
    
    def generate_enum_value(self, enumerator_node):
        parent = self.parents[-1]
        identifier = enumerator_node.name
        value = enumerator_node.value
        if value is not None:
            try:
                if value.value.isdigit():
                    value = int(value.value)
                elif 'x' in value.value:
                    value = int(value.value, 16)
                else:
                    raise ValueError('Uncovertable enum value `%s`' % value.value)
            except Exception, e:
                print e
                value = -42
        return cy_ast.EnumValue(parent, identifier, value)

    def generate_union(self, union_node):
        parent = self.parents[-1]
        identifier = union_node.name
        union = cy_ast.Union(parent, identifier)
        self.parents.append(union)
        for decl in union_node.decls:
            union.add_field(self.generate_field(decl))
        self.parents.pop()
        return union

    def generate_argument(self, decl_node):
        parent = self.parents[-1]
        identifier = decl_node.name
        argument = cy_ast.Argument(parent, identifier)
        self.parents.append(argument)
        argument.typ = self.visit(decl_node.type)
        self.parents.pop()
        return argument

    def generate_func(self, func_node):
        parent = self.parents[-1]
        # need to drill down through the func type until we
        # hit a TypeDecl to get the func name since it may
        # be burried in pointers.
        typ_decl = func_node.type
        while not isinstance(typ_decl, pcp_ast.TypeDecl):
            typ_decl = typ_decl.type
        identifier = typ_decl.declname
        function = cy_ast.Function(parent, identifier)
        self.parents.append(function)
        function.res_type = self.visit(func_node.type)
        for arg in func_node.args.params:
            function.add_argument(self.generate_argument(arg))
        self.parents.pop()
        return function

    def generate_module(self, file_node):
        parent = self.parents[-1]
        module = cy_ast.Module(parent)
        self.parents.append(module)
        for child in file_node.children():
            module.add_item(self.visit(child))
        self.parents.pop()
        return module


