import sys
from pycparser import c_ast as pcp_ast
import cy_ast



class ASTTranslator(object):
    """ Translates a PyCParser AST into a Cython code 
    generation AST.

    """
    def __init__(self):
        # typedef are any typedef, including anymous 
        # structs, unions, and enums
        self.typedefs = {}

        # Non-anonymous structs
        self.structs = {}

        # Non-anonymous unions
        self.unions = {}

        # Non-anonymous enums
        self.enums = {}

        # Function declarations
        self.functions = {}
        
        # A stack of nodes visited while traversing the AST. 
        # The parent node will always be self.node_stack[-2]
        self.node_stack = [None]

    def translate(self, ast):
        self.node_stack = [None]
        return self.visit(ast)

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        self.node_stack.append(node)
        res = visitor(node)
        self.node_stack.pop()
        return res
    
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
        return self.generate_identifier_type(node)
    
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
        fn = self.generate_func(node)
        return fn

    def generate_typedef(self, typedef_node):
        # typedefs can only be def'd once, so if it's already defined,
        # return it.
        identifier = typedef_node.name
        if identifier in self.typedefs:
            return self.typedefs[identifier]

        coord = typedef_node.coord
        location = cy_ast.Location(coord.file, coord.line)
        typedef = cy_ast.Typedef(identifier, location)
        typedef.typ = self.visit(typedef_node.type)

        self.typedefs[identifier] = typedef

        return typedef

    def generate_struct(self, struct_node):
        # If a struct is forward declared it may be visited more than 
        # once. We assume it't not being redefined as the C code that
        # caused such a condition would be uncompilable.
        identifier = struct_node.name
        coord = struct_node.coord
        location = cy_ast.Location(coord.file, coord.line)

        if identifier in self.structs:
            struct = self.structs[identifier]
            struct.location = location
        else:
            struct = cy_ast.Struct(identifier, location)

        if struct_node.decls:
            for decl in struct_node.decls:
                struct.add_field(self.generate_field(decl))

        return struct

    def generate_union(self, union_node):
        # If a union is forward declared it may be visited more than 
        # once. We assume it't not being redefined as the C code that
        # caused such a condition would be uncompilable.
        identifier = union_node.name
        coord = union_node.coord
        location = cy_ast.Location(coord.file, coord.line)
        
        if identifier in self.unions:
            union = self.unions[identifier]
            union.location = location
        else:
            union = cy_ast.Union(identifier, location)
        
        if union_node.decls:
            for decl in union_node.decls:
                union.add_field(self.generate_field(decl))
        
        return union
    
    def generate_enum(self, enum_node):
        # If an enum is forward declared it may be visited more than 
        # once. We assume it't not being redefined as the C code that
        # caused such a condition would be uncompilable.
        identifier = enum_node.name
        coord = enum_node.coord
        location = cy_ast.Location(coord.file, coord.line)

        if identifier in self.enums:
            enum = self.enums[identifiers]
            enum.location = location
        else:
            enum = cy_ast.Enum(identifier, location)
        
        if enum_node.values:
            for value in enum_node.values.enumerators:
                enum.add_field(self.visit(value))

        return enum
    
    def generate_func(self, func_node):
        # Functions should never be receclared, but pointers to them 
        # may get referenced in structs.
        decl_node = self.node_stack[-2]
        identifier = decl_node.name
    
        if identifier in self.functions:
            return self.functions[identifier]
        
        coord = func_code.coord
        location = cy_ast.Location(coord.file, coord.line)
        function = cy_ast.Function(identifier, location)
        function.res_type = self.visit(func_node.type)
        
        for arg in func_node.args.params:
            function.add_argument(self.generate_argument(arg))

        return function

    def generate_field(self, decl_node):
        identifier = decl_node.name
        field = cy_ast.Field(identifier)
        field.typ = self.visit(decl_node.type)
        return field
    
    def generate_enum_value(self, enumerator_node):
        identifier = enumerator_node.name
        value = enumerator_node.value
        if value is not None:
            value = self.eval_enum_value(value)
        return cy_ast.EnumValue(identifier, value)

    def generate_identifier_type(self, type_node):
        # This one is a bit tricky. The .names attribute of an 
        # IdentifierType node will be a list a names that corrspond 
        # to a type e.g. ['unsigned', 'long', 'int']. The problem is 
        # that they are unordered and follow no canonical form
        # (C doesn't require one). Typedef names also appear here,
        # in which case we want to return the typedef node rather
        # than a fundemental type node.
        name = self.canonize_type_names(type_node.names)

        # If the name is a typedef, return the typdef, otherwise
        # assume it's a fundamental type and return that. If it's
        # not found, its either a) an undefined type, b) a modified
        # typedefs such as: typedef int foo; unsigned foo a; We don't
        # handle either case and just fail with an error.
        if name in self.typedefs:
            res = self.typedefs[name]
        else:
            res = cy_ast.C_TYPES.get(name)
            if res is None:
                raise TypeError('Unhandled identifier type `%s`' % name)

        return res

    def generate_pointer(self, ptr_node):
        pointer = cy_ast.Pointer()
        pointer.typ = self.visit(ptr_node.type)
        return pointer

    def generate_array(self, array_node):
        array = cy_ast.Array(int(array_node.dim.value))
        array.typ = self.visit(array_node.type)
        return array

    def generate_argument(self, decl_node):
        identifier = decl_node.name
        argument = cy_ast.Argument(identifier)
        self.parents.append(argument)
        argument.typ = self.visit(decl_node.type)
        return argument

    def generate_module(self, file_node):
        module = cy_ast.Module()
        for child in file_node.children():
            module.add_item(self.visit(child))
        return module

    def eval_enum_value(self, value_node):
        if isinstance(value_node, pcp_ast.UnaryOp):
            res = self.eval_unary_op(value_node)
        elif isinstance(value_node, pcp_ast.BinaryOp):
            res = self.eval_binary_op(value_node)
        elif isinstance(value_node, pcp_ast.Constant):
            res = self.eval_const(value_node)
        else:
            raise TypeError('Unhandled enum value node type `%s`' % value_node)
        return res

    def eval_unary_op(self, unary_node):
        op = unary_node.op
        value = self.eval_const(unary_node.expr)
        if op == '-':
            res = -value
        elif op == '+':
            res = +value
        elif op == '~':
            res = ~value
        else:
            raise ValueError('Unhandled enum unaray op `%s`' % op)
        return res

    def eval_binary_op(self, binary_node):
        op = binary_node.op
        left = self.eval_const(binary_node.left)
        right = self.eval_const(binary_node.right)
        if op == '<<':
            res = left << right
        elif op == '>>':
            res = left >> right
        else:
            raise ValueError('Unhandled enum binary op `%s`.' % op)
        return res

    def eval_const(self, const_node):
        typ = const_node.type
        value = const_node.value
        if typ == 'int':
            if value.isdigit():
                res = int(value)
            elif value.startswith('0x'):
                res = int(value, 16)
            elif value.startswith('0'):
                res = int(value, 8)
            else:
                raise ValueError('Uncovertable enum int value `%s`' % value)
        elif typ == 'float':
            try:
                res = float(value)
            except ValueError:
                raise ValueError('Unconvertable enum float value `%s`' % value)
        elif typ == 'string':
            res = str(value)
        elif typ == 'char':
            res = str(value)
        else:
            raise TypeError('Unhandled enum constant type `%s`' % typ)
        return res

    def canonize_type_names(self, names):
        # Converts a list of names to a canonical form. This assumes
        # a type declaration that is valid C.
        names = names[:]
        if len(names) == 1:
            name = names[0]
            if name == 'signed':
                res = 'int'
            elif name == 'unsigned':
                res = 'unsigned int'
            else:
                res = name
        else:
            ordered = []

            # ignore `signed` because it's implied when it doesn't
            # appear by itself.
            while 'signed' in names:
                names.remove('signed')
            
            # `unsigned` comes first
            if 'unsigned' in names:
                names.remove('unsigned')
                ordered.append('unsigned')

            # exhuast any `long` declarations
            while 'long' in names:
                names.remove('long')
                ordered.append('long')

            # handle 'short'
            if 'short' in names:
                names.remove('short')
                ordered.append('short')

            # the balance of the declaration 
            # goes at the end
            ordered.extend(names)
            
            # if `int` appears along with `short` or `long` we can
            # get rid of the `int` specifier.
            if 'int' in ordered:
                if ('short' in ordered) or ('long' in ordered):
                    ordered.remove('int')

            # join the names with spaces to construct the canonzied
            # form
            res = ' '.join(ordered)

        return res

