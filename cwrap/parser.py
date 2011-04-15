#------------------------------------------------------------------------------
# This file is adapted from ctypeslib.codegen.gccxmlparser
#------------------------------------------------------------------------------
from xml.etree import cElementTree
import os
import sys
import re

import cy_ast


def MAKE_NAME(name):
    name = name.replace('$', 'DOLLAR')
    name = name.replace('.', 'DOT')
    if name.startswith('__'):
        return '_X' + name
    elif name[0] in '01234567879':
        return '_' + name
    return name


WORDPAT = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')


def CHECK_NAME(name):
    if WORDPAT.match(name):
        return name
    return None


class GCCXMLParser(object):

    has_values = set(['Enumeration', 'Function', 'FunctionType',
                      'OperatorFunction', 'Method', 'Constructor',
                      'Destructor', 'OperatorMethod'])

    def __init__(self, *args):
        self.context = []
        self.all = {}
        self.cpp_data = {}

    #--------------------------------------------------------------------------
    # Parsing entry points
    #--------------------------------------------------------------------------
    def parse(self, xmlfile):
        for event, node in cElementTree.iterparse(xmlfile, events=('start', 'end')):
            if event == 'start':
                self.startElement(node.tag, dict(node.items()))
            else:
                if node.text:
                    self.characters(node.text)
                self.endElement(node.tag)
                node.clear()

    def startElement(self, name, attrs):
        # find and call the handler for this element
        mth = getattr(self, 'visit_' + name, None)
        if mth is None:
            result = self.unhandled_element(name, attrs)
        else:
            result = mth(attrs)

        # Record the result and register the the id, which is
        # used in the _fixup_* methods. Some elements don't have
        # and id, so we create our own.
        if result is not None:
            location = attrs.get('location', None)
            if location is not None:
                result.location = location
            _id = attrs.get('id', None)
            if _id is not None:
                self.all[_id] = result
            else:
                self.all[id(result)] = result

        # if this element has children, push onto the context
        if name in self.has_values:
            self.context.append(result)

    cdata = None
    def endElement(self, name):
        # if this element has children, pop the context
        if name in self.has_values:
            self.context.pop()
        self.cdata = None

    def unhandled_element(self, name, attrs):
        print 'Unhandled element `%s`.' % name

    #--------------------------------------------------------------------------
    # Ignored elements and do-nothing handlers
    #--------------------------------------------------------------------------
    def visit_Ignored(self, attrs):
        name = attrs.get('name', None)
        if not name:
            name = attrs.get('mangled', 'UNDEFINED')
        return cy_ast.Ignored(name)

    def _fixup_Ignored(self, const): 
        pass

    visit_Method =  visit_Ignored
    visit_Constructor = visit_Ignored
    visit_Destructor = visit_Ignored
    visit_OperatorMethod  =  visit_Ignored

    _fixup_Method = _fixup_Ignored
    _fixup_Constructor = _fixup_Ignored
    _fixup_Destructor = _fixup_Ignored
    _fixup_OperatorMethod = _fixup_Ignored
    
    visit_Class = lambda *args: None
    visit_Namespace =  lambda *args: None
    visit_Base =  lambda *args: None
    visit_Ellipsis =  lambda *args: None

    #--------------------------------------------------------------------------
    # Revision Handler
    #--------------------------------------------------------------------------
    cvs_revision = None
    def visit_GCC_XML(self, attrs):
        rev = attrs['cvs_revision']
        self.cvs_revision = tuple(map(int, rev.split('.')))

    #--------------------------------------------------------------------------
    # Real element handlers
    #--------------------------------------------------------------------------
    def visit_CPP_DUMP(self, attrs):
        name = attrs['name']
        # Insert a new list for each named section into self.cpp_data,
        # and point self.cdata to it.  self.cdata will be set to None
        # again at the end of each section.
        self.cpp_data[name] = self.cdata = []

    def characters(self, content):
        if self.cdata is not None:
            self.cdata.append(content)

    def visit_File(self, attrs):
        name = attrs['name']
        if sys.platform == 'win32' and ' ' in name:
            # On windows, convert to short filename if it contains blanks
            from ctypes import windll, create_unicode_buffer, sizeof, WinError
            buf = create_unicode_buffer(512)
            if windll.kernel32.GetShortPathNameW(name, buf, sizeof(buf)):
                name = buf.value
        return cy_ast.File(name)

    def _fixup_File(self, f): 
        pass

    def visit_Variable(self, attrs):
        name = attrs['name']
        if name.startswith('cpp_sym_'):
            # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx fix me!
            name = name[len('cpp_sym_'):]
        init = attrs.get('init', None)
        typ = attrs['type']
        return cy_ast.Variable(name, typ, init)

    def _fixup_Variable(self, t):
        t.typ = self.all[t.typ]

    def visit_Typedef(self, attrs):
        name = attrs['name']
        typ = attrs['type']
        return cy_ast.Typedef(name, typ)

    def _fixup_Typedef(self, t):
        t.typ = self.all[t.typ]

    def visit_FundamentalType(self, attrs):
        name = attrs['name']
        if name == 'void':
            size = ''
        else:
            size = attrs['size']
        align = attrs['align']
        return cy_ast.FundamentalType(name, size, align)

    def _fixup_FundamentalType(self, t): 
        pass

    def visit_PointerType(self, attrs):
        typ = attrs['type']
        size = attrs['size']
        align = attrs['align']
        return cy_ast.PointerType(typ, size, align)

    def _fixup_PointerType(self, p):
        p.typ = self.all[p.typ]

    visit_ReferenceType = visit_PointerType
    _fixup_ReferenceType = _fixup_PointerType

    def visit_ArrayType(self, attrs):
        # type, min?, max?
        typ = attrs['type']
        min = attrs['min']
        max = attrs['max']
        if max == 'ffffffffffffffff':
            max = '-1'
        return cy_ast.ArrayType(typ, min, max)

    def _fixup_ArrayType(self, a):
        a.typ = self.all[a.typ]

    def visit_CvQualifiedType(self, attrs):
        # id, type, [const|volatile]
        typ = attrs['type']
        const = attrs.get('const', None)
        volatile = attrs.get('volatile', None)
        return cy_ast.CvQualifiedType(typ, const, volatile)

    def _fixup_CvQualifiedType(self, c):
        c.typ = self.all[c.typ]

    def visit_Function(self, attrs):
        # name, returns, extern, attributes
        name = attrs['name']
        returns = attrs['returns']
        attributes = attrs.get('attributes', '').split()
        extern = attrs.get('extern')
        return cy_ast.Function(name, returns, attributes, extern)

    def _fixup_Function(self, func):
        func.returns = self.all[func.returns]
        func.fixup_argtypes(self.all)

    def visit_FunctionType(self, attrs):
        # id, returns, attributes
        returns = attrs['returns']
        attributes = attrs.get('attributes', '').split()
        return cy_ast.FunctionType(returns, attributes)
    
    def _fixup_FunctionType(self, func):
        func.returns = self.all[func.returns]
        func.fixup_argtypes(self.all)

    def visit_OperatorFunction(self, attrs):
        # name, returns, extern, attributes
        name = attrs['name']
        returns = attrs['returns']
        return cy_ast.OperatorFunction(name, returns)

    def _fixup_OperatorFunction(self, func):
        func.returns = self.all[func.returns]

    #def Method(self, attrs):
    #    # name, virtual, pure_virtual, returns
    #    name = attrs['name']
    #    returns = attrs['returns']
    #    return typedesc.Method(name, returns)

    #def _fixup_Method(self, m):
    #    m.returns = self.all[m.returns]
    #    m.fixup_argtypes(self.all)

    def visit_Argument(self, attrs):
        parent = self.context[-1]
        if parent is not None:
            typ = attrs['type']
            name = attrs.get('name')
            arg = cy_ast.Argument(typ, name)
            parent.add_argument(arg)

    def visit_Enumeration(self, attrs):
        # id, name
        name = attrs['name']
        # If the name isn't a valid Python identifier, create an unnamed enum
        name = CHECK_NAME(name)
        size = attrs['size']
        align = attrs['align']
        return cy_ast.Enumeration(name, size, align)

    def _fixup_Enumeration(self, e): 
        pass

    def visit_EnumValue(self, attrs):
        parent = self.context[-1]
        if parent is not None:
            name = attrs['name']
            value = attrs['init']
            val = cy_ast.EnumValue(name, value)
            parent.add_value(val)

    def _fixup_EnumValue(self, e): 
        pass

    def visit_Struct(self, attrs):
        # id, name, members
        name = attrs.get('name')
        if name is None:
            name = MAKE_NAME(attrs['mangled'])
        bases = attrs.get('bases', '').split()
        members = attrs.get('members', '').split()
        align = attrs['align']
        size = attrs.get('size')
        return cy_ast.Struct(name, align, members, bases, size)

    def _fixup_Struct(self, s):
        s.members = [self.all[m] for m in s.members]
        s.bases = [self.all[b] for b in s.bases]

    def visit_Union(self, attrs):
        name = attrs.get('name')
        if name is None:
            name = MAKE_NAME(attrs['mangled'])
        bases = attrs.get('bases', '').split()
        members = attrs.get('members', '').split()
        align = attrs['align']
        size = attrs.get('size')
        return cy_ast.Union(name, align, members, bases, size)

    def _fixup_Union(self, u):
        u.members = [self.all[m] for m in u.members]
        u.bases = [self.all[b] for b in u.bases]

    def visit_Field(self, attrs):
        # name, type
        name = attrs['name']
        typ = attrs['type']
        bits = attrs.get('bits', None)
        offset = attrs.get('offset')
        return cy_ast.Field(name, typ, bits, offset)

    def _fixup_Field(self, f):
        f.typ = self.all[f.typ]

    def _fixup_Macro(self, m):
        pass
    
    #--------------------------------------------------------------------------
    # Post parsing helpers
    #--------------------------------------------------------------------------
    def get_macros(self, text):
        if text is None:
            return

        # preprocessor definitions that look like macros with one 
        # or more arguments
        text = ''.join(text)
        for m in text.splitlines():
            name, body = m.split(None, 1)
            name, args = name.split('(', 1)
            args = '(%s' % args
            self.all[name] = cy_ast.Macro(name, args, body)

    def get_aliases(self, text, namespace):
        if text is None:
            return
        
        # preprocessor definitions that look like aliases:
        #  #define A B
        text = ''.join(text)
        aliases = {}
        for a in text.splitlines():
            name, value = a.split(None, 1)
            a = cy_ast.Alias(name, value)
            aliases[name] = a
            self.all[name] = a

        # The alias value will be located in the namespace,
        # or the aliases. Otherwise, it's unfound.
        for name, a in aliases.items():
            value = a.value
            if value in namespace:
                a.typ = namespace[value]
            elif value in aliases:
                a.typ = aliases[value]
            else:
                pass

    def get_result(self):
        # Drop some warnings for early gccxml versions
        import warnings
        if self.cvs_revision is None:
            warnings.warn('Could not determine CVS revision of GCCXML')
        elif self.cvs_revision < (1, 114):
            warnings.warn('CVS Revision of GCCXML is %d.%d' % self.cvs_revision)

        # Gather any macros.
        self.get_macros(self.cpp_data.get('functions'))

        # Pass through all the items, hooking up the appropriate 
        # links by replacing the id tags with the actual objects
        remove = []
        for name, node in self.all.items():
            location = getattr(node, 'location', None)
            if location is not None:
                fil, line = location.split(':')
                node.location = (self.all[fil].name, line)
            method_name = '_fixup_' + node.__class__.__name__
            fixup_method = getattr(self, method_name, None)
            if fixup_method is not None:
                fixup_method(node)
            else:
                remove.append(node)
        
        # remove any nodes don't have handler methods
        for n in remove:
            del self.all[n]

        # Now we can build the namespace, keeping only the nodes
        # in which we're interested.
        interesting = (cy_ast.Typedef, cy_ast.Enumeration, cy_ast.EnumValue,
                       cy_ast.Function, cy_ast.Struct, cy_ast.Union,
                       cy_ast.Variable, cy_ast.Macro, cy_ast.Alias)
        
        namespace = {}
        for node in self.all.values():
            if not isinstance(node, interesting):
                continue  # we don't want these
            name = getattr(node, 'name', None)
            if name is not None:
                namespace[name] = node

        self.get_aliases(self.cpp_data.get('aliases'), namespace)

        result = []
        for node in self.all.values():
            if isinstance(node, interesting):
                result.append(node)

        return result


def parse(xmlfile):
    # parse an XML file into a sequence of type descriptions
    parser = GCCXMLParser()
    parser.parse(xmlfile)
    items = parser.get_result()
    in_name = os.path.split(xmlfile)[-1].replace('xml', 'h')
    res = []
    for item in items:
        if item.location:
            out_name = os.path.split(item.location[0])[-1]
            if out_name == in_name:
                res.append(item)
    res.sort(key=lambda item: int(item.location[1]))
    return res
