# inspired by http://eli.thegreenplace.net/2011/07/03/parsing-c-in-python-with-clang/

import sys, os
import clang.cindex
libpath, foo = os.path.split(clang.cindex.__file__)
clang.cindex.Config.set_library_path(libpath)
#put libclang.dylib(.so, .dll) into clang package directory)
from clang.cindex import TypeKind, CursorKind

def verbose(*args, **kwargs):
    '''filter predicate for show_ast: show all'''
    return True

def no_system_includes(cursor, level):
    '''filter predicate for show_ast: filter out verbose stuff from system include files'''
    return (level!= 1) or (cursor.location.file is not None and not cursor.location.file.name.startswith('/usr/include'))

# A function show(level, *args) would have been simpler but less fun
# and you'd need a separate parameter for the AST walkers if you want it to be exchangeable.
class Level(int):
    '''represent currently visited level of a tree'''
    def show(self, *args):
        '''pretty print an indented line'''
        print '\t'*self + ' '.join(map(str, args))
    def __add__(self, inc):
        '''increase level'''
        return Level(super(Level, self).__add__(inc))

def is_valid_type(t):
    '''used to check if a cursor has a type'''
    return t.kind != clang.cindex.TypeKind.INVALID
    
def qualifiers(t):
    '''set of qualifiers of a type'''
    q = set()
    if t.is_const_qualified(): q.add('const')
    if t.is_volatile_qualified(): q.add('volatile')
    if t.is_restrict_qualified(): q.add('restrict')
    return q

def show_type(t, level, title):
    '''pretty print type AST'''
    level.show(title, str(t.kind), ' '.join(qualifiers(t)))
    #level.show(title, str(t.get_canonical().kind))
    if is_valid_type(t.get_pointee()):
        show_type(t.get_pointee(), level+1, 'points to:')
    
    if t.kind is TypeKind.CONSTANTARRAY:
        show_type(t.element_type, level+1, 'array element type:')
        #level.show('size:', t.get_array_size())
        level.show('size:', t.element_count)
        
    if t.kind is TypeKind.UNEXPOSED:
        canonical_type = t.get_canonical()
        if canonical_type.kind is not TypeKind.UNEXPOSED:
            show_type(canonical_type, level+1, 'canonical type')

def show_comment(comment, level):
    level.show('comment kind', comment.kind, repr(comment.text()))
    for c in comment.children():
        show_comment(c, level+1)

    

def show_ast(cursor, filter_pred=verbose, level=Level()):
    '''pretty print cursor AST'''
    if filter_pred(cursor, level):
        print
        level.show(cursor.kind, 
                   repr(cursor.spelling), 
                   repr(cursor.displayname), 
                   #cursor.location,
                   #cursor.extent,
                   )
        #T = ' '.join([t.spelling for t in cursor.get_tokens()][:-1]) #one token too much?
        #level.show('token: ', T)

        if cursor.get_brief_comment_text() is not None:
            level.show('#', cursor.get_brief_comment_text())
        if cursor.get_raw_comment_text():
            #level.show('##', cursor.get_raw_comment_text())
            comment = cursor.get_parsed_comment()
            show_comment(comment, level)
            
        if cursor.kind.is_preprocessing():
            print "PREPROCESSING"
            print cursor.location
            T = '|'.join([t.spelling for t in cursor.get_tokens()][:-1]) #one token too much?
            level.show('token: ', T)


        if is_valid_type(cursor.type):
            show_type(cursor.type, level+1, 'type:')
            #show_type(cursor.type.get_canonical(), level+1, 'canonical type:')

        if cursor.kind is CursorKind.ENUM_CONSTANT_DECL:
            level.show('value:', cursor.enum_value)

        if cursor.kind is CursorKind.INTEGER_LITERAL:
            level.show([t.spelling for t in cursor.get_tokens()][:-1])

        if cursor.kind is CursorKind.FUNCTION_DECL:
            show_type(cursor.result_type, level+1, 'result type:')
            t = cursor.type
            for k, arg in enumerate(t.argument_types()):
                show_type(arg, level+1, 'argument %d'%k)

        if cursor.kind is CursorKind.TYPEDEF_DECL:
            show_type(cursor.underlying_typedef_type, level+1, 'typedef type')
            (level+1).show('typedef type declaration:', cursor.underlying_typedef_type.get_declaration().spelling, )


        for c in cursor.get_children():
            show_ast(c, filter_pred, level+1)

def print_diag_info(diag):
    print 'location:', diag.location
    print 'severity:', diag.severity
    print 'spelling:', diag.spelling
    print 'ranges:', list(diag.ranges)
    print 'fixits', list(diag.fixits)
    print 'category name:', diag.category_name
    print


if __name__ == '__main__':
    index = clang.cindex.Index.create()
    tu = index.parse(sys.argv[1],
                     #args = '-x c',
                     options = clang.cindex.TranslationUnit.PARSE_INCOMPLETE + \
                         clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD + \
                         #clang.cindex.TranslationUnit.PARSE_INCLUDE_BRIEF_COMMENTS_IN_CODE_COMPLETION + \
                         clang.cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
                     )
    print "Translation unit: '%s'"%(tu.spelling,)
    print "Includes: "
    for f in tu.get_includes():
        print '\t'*f.depth, f.include.name
    print "---"

    print "Diagnostics:"
    for d in tu.diagnostics:
        print_diag_info(d)
    print "---"

    print "AST:"
    show_ast(tu.cursor, no_system_includes)
