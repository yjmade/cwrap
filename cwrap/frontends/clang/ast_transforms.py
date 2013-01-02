# CWrap imports
from cwrap.backend import cw_ast
from cwrap.config import ASTContainer 

# Local package imports
import c_ast


def find_toplevel_items(items):
    """ Finds and returns the toplevel items given a list of items, one
    of which should be a toplevel namespace node.

    """
    # for item in items:
    #     if isinstance(item, c_ast.Namespace):
    #         if item.name == '::':
    #             toplevel_ns = item
    #             break
    # else:
    #     raise RuntimeError('Toplevel namespace not found.')
    
    # res_items = []
    # return toplevel_ns.members[:]
    return items
    
def sort_toplevel_items(items):
    """ Sorts the items first by their filename, then by lineno. Returns
    a new list of items

    """
    key = lambda node: node.location
    return sorted(items, key=key)


def _flatten_container(container, items=None, context_name=None):
    """ Given a struct or union, replaces nested structs or unions
    with toplevel struct/unions and a typdef'd member. This will 
    recursively expand everything nested. The `items` and `context_name`
    arguments are used internally. Returns a list of flattened nodes.

    """
    if items is None:
        items = []

    parent_context = container.context
    parent_name = container.name

    mod_context = []
    for i, field in enumerate(container.members):
        if isinstance(field, (c_ast.Struct, c_ast.Union)):
            # Create the necessary mangled names
            mangled_name = '__%s_%s' % (parent_name, field.name)
            mangled_typename = mangled_name + '_t'
            
            # Change the name of the nested item to the mangled
            # item the context to the parent context
            field.name = mangled_name
            field.context = parent_context
            
            # Expand any nested definitions for this container.
            _flatten_container(field, items, parent_name)
            
            # Create a typedef for the mangled name with the parent_context
            typedef = c_ast.Typedef(mangled_typename, field, parent_context)
                
            # Add the typedef to the list of items
            items.append(typedef)

            # Add the necessary information to the mod_context so 
            # we can modify the list of members at the end.
            mod_context.append((i, field, typedef))

    # Use the mod_context to remove the nest definitions and replace 
    # any fields that reference them with the typedefs.
    for idx, field, typedef in reversed(mod_context):
        container.members.pop(idx)
        for member in container.members:
            if isinstance(member, c_ast.Field):
                if member.typ is field:
                    member.typ = typedef

    items.append(container)

    return items


def flatten_nested_containers(items):
    """ Searches for Struct/Union nodes with nested Struct/Union 
    definitions, when it finds them, it creates a similar definition
    in the namespace with an approprately mangled name, and reorganizes 
    the nodes appropriately. This is required since Cython doesn't support 
    nested definitions. Returns a new list of items. 
    
    """
    res_items = []
    for node in items:
        if not isinstance(node, (c_ast.Struct, c_ast.Union)):
            res_items.append(node)
        else:
            res_items.extend(_flatten_container(node))
    return res_items
                    
           
def _ignore_filter(node):
    return not isinstance(node, c_ast.Ignored)


def _location_filter(node):
    return node.location is not None


def _ignore_and_location_filter(node):
    return _ignore_filter(node) and _location_filter(node)


def filter_ignored(items):
    """ Searches a list of toplevel items and removed any instances
    of c_ast.Ignored nodes. Node members are search as well. Returns
    a new list of items.

    """
    res_items = filter(_ignore_and_location_filter, items)
    for item in res_items:
        if isinstance(item, (c_ast.Struct, c_ast.Union)):
            item.members = filter(_ignore_filter, item.members)
        elif isinstance(item, c_ast.Enumeration):
            item.values = filter(_ignore_filter, item.values)
        elif isinstance(item, (c_ast.Function, c_ast.FunctionType)):
            item.arguments = filter(_ignore_filter, item.arguments)
    return res_items


def apply_c_ast_transformations(c_ast_items):
    """ Applies the necessary transformations to a list of c_ast nodes
    which are the output of the gccxml_parser. The returned list of items
    are appropriate for passing the CAstTransformer class.

    The following transformations are applied:
        1) find and extract the toplevel items
        2) sort the toplevel items into the order they appear
        3) extract and replace nested structs and unions
        4) get rid of any c_ast.Ignored nodes

    """
    items = find_toplevel_items(c_ast_items)
    items = sort_toplevel_items(items)
    items = flatten_nested_containers(items)
    items = filter_ignored(items)
    return items


class CAstContainer(object):
    """ A container object that holds a list of ast items, and the
    names of the modules they should be rendered to.

    """
    def __init__(self, items, header_name, extern_name, implementation_name):
        self.items = items
        self.header_name = header_name
        self.extern_name = extern_name
        self.implementation_name = implementation_name


class CAstTransformer(object):

    def __init__(self, ast_containers):
        # XXX - work out the symbols
        self.ast_containers = ast_containers
        self.pxd_nodes = []
        self.modifier_stack = []

    def transform(self):
        for container in self.ast_containers:
            items = container.items
            self.pxd_nodes = []
            self.modifier_stack = []
            header_name = container.header_name

            for item in items:
                # only transform items for this header (not #include'd
                # or other __builtin__ stuff)
                if item.location is not None:
                    if not item.location[0].endswith(header_name):
                        continue
                self.visit(item)
       
            extern = cw_ast.ExternFrom(container.header_name, self.pxd_nodes)
            cdef_decl = cw_ast.CdefDecl([], extern)
            mod = cw_ast.Module([cdef_decl])
            
            yield ASTContainer(mod, container.extern_name + '.pxd')

    def visit(self, node):
        visitor_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, visitor_name, self.generic_visit)
        res = visitor(node)
        return res

    def generic_visit(self, node):
        print 'unhandled node in generic_visit: %s' % node
       
    #--------------------------------------------------------------------------
    # Toplevel visitors
    #--------------------------------------------------------------------------
    def visit_Struct(self, struct):
        name = struct.name
        body = []
        for member in struct.members:
            body.append(self.visit_translate(member))
        if not body:
            body.append(cw_ast.Pass)
        struct_def = cw_ast.StructDef(name, body)
        cdef = cw_ast.CdefDecl([], struct_def)
        self.pxd_nodes.append(cdef)

    def visit_Union(self, union):
        name = union.name
        body = []
        for member in union.members:
            body.append(self.visit_translate(member))
        if not body:
            body.append(cw_ast.Pass)
        union_def = cw_ast.UnionDef(name, body)
        cdef = cw_ast.CdefDecl([], union_def)
        self.pxd_nodes.append(cdef)

    def visit_Enumeration(self, enum):
        name = enum.name
        body = []
        for value in enum.values:
            body.append(self.visit_translate(value))
        if not body:
            body.append(cw_ast.Pass)
        enum_def = cw_ast.EnumDef(name, body)
        cdef = cw_ast.CdefDecl([], enum_def)
        self.pxd_nodes.append(cdef)

    def visit_Function(self, func):
        name = func.name
        args = []
        for arg in func.arguments:
            args.append(self.visit_translate(arg))
        args = cw_ast.arguments(args, None, None, [])
        returns = self.visit_translate(func.returns)
        func_def = cw_ast.CFunctionDecl(name, args, returns, None)
        self.pxd_nodes.append(func_def)

    def visit_Variable(self, var):
        name = var.name
        type_name = self.visit_translate(var.typ)
        expr = cw_ast.Expr(cw_ast.CName(type_name, name))
        self.pxd_nodes.append(expr)

    def visit_Typedef(self, td):
        name = td.name #typedef name
        
        type_name = self.visit_translate(td.typ)
        expr = cw_ast.Expr(cw_ast.CName(type_name, name))
        
        #extended ctypedef of enums/struct/union:
        if isinstance(td.typ, (c_ast.Enumeration, )): 
                      #td.typ.__class__.__name__ in ('Enumeration',):
            tag_name = td.typ.name
            body = [self.visit_translate(value) for value in td.typ.values]
            if not body:
                body.append(cw_ast.Pass)
            ext_expr = cw_ast.EnumDef(name, body) #TODO: analogue to visit_Enumeration for struct etc.
            print 'tag_name:', repr(tag_name), 'name:', repr(name)
        
            ctypedef = cw_ast.CTypedefDecl(ext_expr)
            self.pxd_nodes.append(ctypedef)
            # if not tag_name:
            #     #removed = self.pxd_nodes.pop() #drop previous enum #TODO: assert, TODO: order might be scrambled!!
            #     #print "in visit_Typedef: removed", type(removed) 
            #     self.pxd_nodes.append(ctypedef)
            # elif tag_name == name:
            #     pass
            # else: #tag_name not empty and different
            #     self.pxd_nodes.append(cw_ast.CTypedefDecl(expr)) #simple ctypedef
        else:
            ctypedef = cw_ast.CTypedefDecl(expr)
            self.pxd_nodes.append(ctypedef)
        

        print "visit typedef:", repr(name), td.typ


    #--------------------------------------------------------------------------
    # render nodes
    #--------------------------------------------------------------------------
    def visit_translate(self, node):
        name = 'translate_' + node.__class__.__name__
        res = getattr(self, name, lambda arg: None)(node)
        if res is None:
            print 'Unhandled node in translate: ', node
        return res

    def translate_Field(self, field):
        name = field.name
        type_name = self.visit_translate(field.typ)
        return cw_ast.Expr(cw_ast.CName(type_name, name))

    def translate_Enumeration(self, enum):
        name = enum.name
        return cw_ast.TypeName(cw_ast.Name(name, cw_ast.Param))

    def translate_EnumValue(self, value):
        name = value.name
        return cw_ast.Expr(cw_ast.Name(name, cw_ast.Param))

    def translate_Struct(self, struct):
        name = struct.name
        return cw_ast.TypeName(cw_ast.Name(name, cw_ast.Param))

    def translate_Union(self, union):
        name = union.name
        return cw_ast.TypeName(cw_ast.Name(name, cw_ast.Param))

    def translate_Argument(self, arg):
        name = arg.name
        type_name = self.visit_translate(arg.typ)
        if name is None:
            name = ''
        cname = cw_ast.CName(type_name, name)
        return cname
        
    def translate_PointerType(self, pointer):
        return cw_ast.Pointer(self.visit_translate(pointer.typ))

    def translate_ArrayType(self, array):
        min = int(array.min)
        max = int(array.max)
        dim = max - min + 1
        return cw_ast.Array(self.visit_translate(array.typ), dim)
    
    def translate_CvQualifiedType(self, qual):
        return self.visit_translate(qual.typ)

    def translate_Typedef(self, typedef):
        return cw_ast.TypeName(cw_ast.Name(typedef.name, cw_ast.Param))

    def translate_FundamentalType(self, fund_type):
        return cw_ast.TypeName(cw_ast.Name(fund_type.name, cw_ast.Param))

    def translate_FunctionType(self, func_type):
        args = []
        for arg in func_type.arguments:
            args.append(self.visit_translate(arg))
        args = cw_ast.arguments(args, None, None, [])
        returns = self.visit_translate(func_type.returns)
        func_type = cw_ast.CFunctionType(args, returns)
        return func_type
    
