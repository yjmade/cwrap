from collections import defaultdict

from cStringIO import StringIO
import cy_ast


class Code(object):

    def __init__(self):
        self._io = StringIO()
        self._indent_level = 0
        self._indentor = '    '
        self._imports = defaultdict(set)
        self._imports_from = defaultdict(lambda: defaultdict(set))
        self._cimports = defaultdict(set)
        self._cimports_from = defaultdict(lambda: defaultdict(set))

    def indent(self, n=1):
        self._indent_level += n

    def dedent(self, n=1):
        self._indent_level -= n

    def write_i(self, code):
        indent = self._indentor * self._indent_level
        self._io.write('%s%s' % (indent, code))

    def write(self, code):
        self._io.write(code)

    def add_import(self, module, as_name=None):
        self._imports[module].add(as_name)

    def add_import_from(self, module, imp_name, as_name=None):
        self._imports_from[module][imp_name].add(as_name)

    def add_cimport(self, module, as_name=None):
        self._cimports[module].add(as_name)
    
    def add_cimport_from(self, module, imp_name, as_name=None):
        self._cimports_from[module][imp_name].add(as_name)

    def code(self):
        return '#imports\n' + self._io.getvalue()


class CodeRenderer(object):

    def __init__(self):
        self.node_stack = [None]
        self.extern_io = None
        self.pxd_io = None
        self.pyx_io = None
    
    def render(self, module, header):
        """ Renders the items from the module ast only if those
        items exist in the given header (Since the ast will contain
        items from headers that were #included).

        """
        self.node_stack = [None]
        self.extern_code = Code()
        self.pxd_code = Code()
        self.pyx_code = Code()

        for item in module.items:
            if item.location.header == header:
                self.visit(item)

        extern_code = self.header_code.code()
        pxd_code = self.pxd_code.code()
        pyx_code = self.pyx_code.code()

        return extern_code, pxd_code, pyx_code

    def visit(self, node):
        self.node_stack.append(node)
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        visitor(node)
        self.node_stack.pop()

    def generic_visit(self, node):
        print 'unhandled node', type(node)

    def visit_Typedef(self, node):
        # delegate the typedef to the child, which will 
        # properly handle a typedef situation
        self.visit(node.typ)

    def visit_Struct(self, node):
        self.render_struct(node)

    def _render_struct_property_get(field, code):
        code.write_i('def __get__(self):\n')
        code.indent()
        name = field.identifier
        c_type = field.typ.c_type()
        code.write_i('cdef %s %s = self.%s\n' % (c_type, name, name))
        code.write_i('return %s\n\n' % field.typ.c_var_to_object(name))
        code.dedent()
        
    def _render_struct_property_set(field, code):
        name = field.identifier
        code.write_i('def __set__(self, %s):\n' % name)
        code.indent()
        c_type = field.typ.c_type()
        convert = field.typ.object_var_to_c(name)
        code.write_i('cdef %s cval = %s\n' % (c_type, convert))
        code.write_i('self.%s = cval\n\n' % name)
        code.dedent()

    def _render_struct_property(field, code):
        name = field.identifier
        code.write_i('property %s:\n\n' % name)
        code.indent()
        if 'r' in field.mode:
            _render_struct_property_get(field, code)
        if 'w' in field.mode:
            _render_struct_property_set(field, code)
        code.dedent()

    def _render_struct_impl(struct, code):
        name = struct.identifier
        code.write_i('cdef class %s:\n\n' % name)
        code.indent()
        code.write_i('def __cinit__(self):\n')
        code.indent()
        code.write_i('self.thisptr = <%s*>PyMem_Malloc(sizeof(%s))\n\n' % (name, name))
        code.dedent()
        code.write_i('def __dealloc__(self):\n')
        code.indent()
        code.write_i('PyMem_Free(self.thisptr)\n\n')
        code.dedent()
        for field in struct.fields:
            _render_struct_property(field, code)
        code.dedent()

    def _render_struct_def(self, struct):
        name = struct.identifier
        code.write_i('cdef class %s:\n\n' % name)
        code.indent()
        code.write_i('cdef %s* thisptr\n\n' % name)
        code.dedent()

    def _render_extern_struct_field(self, field):
        name = field.identifier
        if issubclass(field.typ, cy_ast.CType):
            c_name = field.typ.c_name
        elif ise(field.typ, cy_ast.Typedef):
            c_name = field.typ.identifier
        else:
            raise TypeError('Unhandled field type `%s`.' % field.typ)
        self.extern_code.write_i('%s %s\n' % (c_name, name))

    def _extern_struct_field_loop(self, struct):
        self.extern_code.indent()
        for field in struct.fields:
            self._render_extern_struct_field(field)
        self.extern_code.dedent()

    def _render_extern_struct(self, struct):
        st_name = struct.identifier
        parent = self.node_stack[-2]
        if isinstance(parent, cy_ast.Typedef):
            td_name = parent.identifier
            if td_name == st_name:
                if struct.opaque:
                    self.extern_code.write_i('cdef struct %s\n' % st_name)
                else:
                    self.extern_code.write_i('cdef struct %s:\n' % st_name)
                    self._extern_struct_field_loop(struct)
            elif st_name is None:
                if struct.opaque:
                    self.extern_code.write_i('ctypedef struct %s\n' % td_name)
                else:
                    self.extern_code.write_i('ctypdef struct %s:\n' % td_name)
                    self._extern_struct_field_loop(struct)
            else:
                if struct.opaque:
                    self.extern_code.write_i('cdef struct %s' % st_name)
                else:
                    self.extern_code.write_i('cdef struct %s:\n' % st_name)
                    self._extern_struct_field_loop(struct)
                self.extern_code.write_i('ctypedef %s %s\n' % (st_name, td_name))
        else:
            if struct.opaque:
                self.extern_code.write_i('cdef struct %s' % st_name)
            else:
                self.extern_code.write_i('cdef struct %s:\n' % st_name)
                self._extern_struct_field_loop(struct)
        self.extern_code.write('\n')

    def render_struct(self, struct):
        self._render_extern_struct(struct)
        #self._render_struct_def(struct)
        #self._render_struct_impl(struct)


#------------------------------------------------------------------------------
# Union
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Enum
#------------------------------------------------------------------------------

def _render_enum_value(enum_value, last_value, code):
    name = enum_value.identifier
    value = enum_value.value
    if value is None:
        value = last_value + 1
    code.write_i('%s = %s\n' % (name, value))
    return value


def _render_enum_impl(enum, code):
    last_value = -1
    for value in enum.values:
        last_value = _render_enum_value(value, last_value, code)
    code.write_i('\n')


def _render_extern_enum_value(enum_value, code):
    name = enum_value.identifier
    code.write_i('%s\n' % name)


def _extern_enum_value_loop(enum, code):
    code.indent()
    for value in enum.values:
        _render_extern_enum_value(value, code)
    code.dedent()


def _render_extern_enum(enum, code):
    en_name = enum.identifier
    if isinstance(enum.parent, cy_ast.Typedef):
        td_name = enum.parent.identifier
        if td_name == en_name:
            code.write_i('cdef enum %s:\n' % en_name)
            _extern_enum_value_loop(enum, code)
        elif en_name is None:
            code.write_i('ctypdef enum %s:\n' % td_name)
            _extern_enum_value_loop(enum, code)
        else:
            code.write_i('cdef enum %s:\n' % en_name)
            _extern_enum_value_loop(enum, code)
            code.write_i('ctypedef %s %s\n' % (en_name, td_name))
    else:
        code.write_i('cdef enum %s:\n' % en_name)
        _extern_enum_value_loop(enum, code)
    code.write('\n')


def render_enum(enum, extern_code, pxd_code, pyx_code):
    # Enum's don't need to be written to pxd files
    _render_extern_enum(enum, extern_code)
    _render_enum_impl(enum, pyx_code)


#------------------------------------------------------------------------------
# Typedef
#------------------------------------------------------------------------------

def render_typedef(typedef, extern_code, pxd_code, pyx_code):
    if isinstance(typedef.typ, cy_ast.Struct):
        render_struct(typedef.typ, extern_code, pxd_code, pyx_code)
    elif isinstance(typedef.typ, cy_ast.Enum):
        render_enum(typedef.typ, extern_code, pxd_code, pyx_code)
    elif isinstance(typedef.typ, cy_ast.Typedef):
        render_typedef(typedef.typ, extern_code, pxd_code, pyx_code)


#------------------------------------------------------------------------------
# Function
#------------------------------------------------------------------------------

