# CWrap imports
from ...backend import cw_ast
from ...config import ASTContainer

# Local package imports
from . import c_ast


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

    #return items
    #TODO:
    ##print 'get toplevel items'
    #print 'items', items
    for item in items:
        if isinstance(item, c_ast.File):
            #print 'toplevel', item
            #print item.members
            return item.members


def sort_toplevel_items(items):
    """ Sorts the items first by their filename, then by lineno. Returns
    a new list of items

    """
    key = lambda node: node.location
    return sorted(items, key=key)


def _flatten_container(container, items=None): #, context_name=None):
    """ Given a struct or union, replaces nested structs or unions
    with toplevel struct/unions and a typdef'd member. This will
    recursively expand everything nested. The `items` and `context_name`
    arguments are used internally. Returns a list of flattened nodes.

    """
    #print '_flatten_container_start', container.__class__.__name__, container.name
    #print [(m.__class__.__name__, m.name) for m in container.members]


    if items is None:
        items = []

    parent_context = container.context
    parent_name = container.name
    if not parent_name:
        parent_name = container.typedef_name

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
            _flatten_container(field, items) #, parent_name)

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
        r = container.members.pop(idx) #TODO????
        print('removed member', r.name)
        for member in container.members:
            if isinstance(member, c_ast.Field):
                if member.typ is field:
                    member.typ = typedef

    items.append(container) #removed for typedef???

    #print '_flatten_container_end: items', [(item.__class__.__name__, item.name) for item in items]


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
        if isinstance(node, (c_ast.Struct, c_ast.Union)):
            res_items.extend(_flatten_container(node))
        elif isinstance(node, c_ast.Typedef):
            #print 'found Typedef', node.typ
            r = flatten_nested_containers([node.typ])
            #print 'flattened typedef type:', r
            # When the flatting didn't introduce any change, just append
            # the original node, as it was. An example is:
            # 'typedef struct foo bar'
            if len(r) == 1 and node.typ == r[0]:
                res_items.append(node)
            else:
                res_items.extend(r[:-1])
                res_items.append(node)
        else:
            res_items.append(node)
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
    res_items = list(filter(_ignore_and_location_filter, items))
    for item in res_items:
        if isinstance(item, (c_ast.Struct, c_ast.Union)):
            item.members = list(filter(_ignore_filter, item.members))
        elif isinstance(item, c_ast.Enumeration):
            item.values = list(filter(_ignore_filter, item.values))
        elif isinstance(item, (c_ast.Function, c_ast.FunctionType)):
            item.arguments = list(filter(_ignore_filter, item.arguments))
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
    #print 'in ast_transforms, toplevel_items:'
    for item in items:
        pass
        #print item.__class__.__name__, item.name
    #print '#end toplevel_items '
    #items = sort_toplevel_items(items)
    items = flatten_nested_containers(items)
    #items = filter_ignored(items)
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
                    #if not item.location[0].endswith(header_name):
                    #    continue
                    pass #include everythin
                self.visit(item)
                #TODO: debug only
                #print self.pxd_nodes
                #print

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
        pass
        #print 'unhandled node in generic_visit: %s' % node

    #--------------------------------------------------------------------------
    # Toplevel visitors
    #--------------------------------------------------------------------------
    def visit_Struct(self, struct):
        name = struct.name
        body = []
        for member in struct.members:
            #body.append(self.visit_translate(member))

            m = self.visit_translate(member)
            if m is not None:
                if isinstance(m, cw_ast.stmt):
                    #print "append to struct:", name, "member:", type(m)
                    body.append(m)
                else:
                    #print "omitting", m, "from class", name
                    pass


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
        #print "visit typedef:", td.typ.__class__.__name__, repr(td.typ.name), repr(name)

        #extended ctypedef of enums/struct/union:
        #TODO: refactor into common function
        #ctypedef of unnamed enumeration, struct, union: include members
        if isinstance(td.typ, c_ast.Enumeration) and not td.typ.name:
            tag_name = td.typ.name
            body = [self.visit_translate(value) for value in td.typ.values]
            if not body:
                body = [cw_ast.Pass,]
            ext_expr = cw_ast.EnumDef(name, body)
            ctypedef = cw_ast.CTypedefDecl(ext_expr)
            self.pxd_nodes.append(ctypedef)

        elif isinstance(td.typ, c_ast.Struct) and not td.typ.name:
            tag_name = td.typ.name
            body = [self.visit_translate(member) for member in td.typ.members ]
            if not body:
                body = [cw_ast.Pass,]
            ext_expr = cw_ast.StructDef(name, body)
            #print 'tag_name:', repr(tag_name), 'name:', repr(name)
            ctypedef = cw_ast.CTypedefDecl(ext_expr)
            self.pxd_nodes.append(ctypedef)

        elif isinstance(td.typ, c_ast.Union) and not td.typ.name:
            tag_name = td.typ.name
            body = [self.visit_translate(member) for member in td.typ.members ]
            if not body:
                body = [cw_ast.Pass,]
            ext_expr = cw_ast.UnionDef(name, body)
            #print 'tag_name:', repr(tag_name), 'name:', repr(name)
            ctypedef = cw_ast.CTypedefDecl(ext_expr)
            self.pxd_nodes.append(ctypedef)

        else:
            type_name = self.visit_translate(td.typ)
            expr = cw_ast.Expr(cw_ast.CName(type_name, name))
            ctypedef = cw_ast.CTypedefDecl(expr)
            self.pxd_nodes.append(ctypedef)

        #print

    def visit_Class(self, klasse):
        name = klasse.name
        body = []
        for member in klasse.members:
            m = self.visit_translate(member)
            #body.append(self.visit_translate(member))
            if m is not None:
                if isinstance(m, cw_ast.stmt):
                    #print "append class:", name, "member:", type(m)
                    body.append(m)
                else:
                    #print "omitting", m, "from class", name
                    pass

        if not body:
            body.append(cw_ast.Pass)
        class_def = cw_ast.CppClassDef(name, body)
        cdef = cw_ast.CdefDecl([], class_def)
        self.pxd_nodes.append(cdef)

    def visit_Namespace(self, ns):
        #TODO: implement Namespacing handling
        body = []
        for member in ns.members:
            t = self.visit(member)

    #--------------------------------------------------------------------------
    # render nodes
    #--------------------------------------------------------------------------
    def visit_translate(self, node):
        name = 'translate_' + node.__class__.__name__
        res = getattr(self, name, lambda arg: None)(node)
        if res is None:
            #print 'Unhandled node in translate: ', node
            pass
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
        if not name and hasattr(struct, 'typedef_name'):
            name = struct.typedef_name
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

    def translate_RefType(self, ref):
        return cw_ast.Reference(self.visit_translate(ref.typ))

    def translate_ArrayType(self, array):
        min = int(array.min)
        max = int(array.max)
        dim = max - min + 1
        return cw_ast.Array(self.visit_translate(array.typ), dim)

    def translate_CvQualifiedType(self, qual):
        # The `const` and `volatile` attributes are defined for `TypeName`
        # and `Pointer`
        cvtype = self.visit_translate(qual.typ)
        cvtype.const = qual.const
        cvtype.volatile = qual.volatile
        return cvtype

    def translate_Typedef(self, typedef):
        return cw_ast.TypeName(cw_ast.Name(typedef.name, cw_ast.Param))

    def translate_FundamentalType(self, fund_type):
        return cw_ast.TypeName(cw_ast.Name(fund_type.name, cw_ast.Param))

    def translate_FunctionType(self, func_type):
        args = []
        for arg in func_type.arguments:
            # This case happens e.g. when an enum is used as function
            # parameter
            if not arg.typ.name and hasattr(arg.typ, 'typedef_name'):
                arg.typ.name = arg.typ.typedef_name
            args.append(self.visit_translate(arg))
        args = cw_ast.arguments(args, None, None, [])
        returns = self.visit_translate(func_type.returns)
        func_type = cw_ast.CFunctionType(args, returns)
        return func_type

    def translate_Class(self, klass):
        name = klass.name
        return cw_ast.TypeName(cw_ast.Name(name, cw_ast.Param))

    def translate_Function(self, func):
        name = func.name
        args = []
        for arg in func.arguments:
            args.append(self.visit_translate(arg))
        args = cw_ast.arguments(args, None, None, [])
        returns = self.visit_translate(func.returns)
        func_def = cw_ast.CFunctionDecl(name, args, returns, None)
        return func_def


