import cy_ast


def find_toplevel_ns(items):
    """ Finds and returns the toplevel namespace given a list of items.

    """
    for item in items:
        if isinstance(item, cy_ast.Namespace):
            if item.name == '::':
                toplevel_ns = item
                break
    else:
        raise RuntimeError('Toplevel namespace not found.')
    
    return toplevel_ns

    
def sort_ns(ns):
    """ Sorts the members of a namespace first by their filename, then 
    by lineno.

    """
    key = lambda node: node.location
    ns.members.sort(key=key)


def transform_nested_structs(items, ns):
    """ Searches for Struct/Union nodes with nested Struct/Union 
    definitions, when it finds them, it creates a similar definition
    in the namespace with an approprately mangled name, and reorganizes 
    the nodes appropriately. This is required since Cython doesn't support 
    nested definitions. The namespace should already have its items sorted 
    before calling this function.
    
    """
    inserts = []
    for node in items:
        if isinstance(node, (cy_ast.Struct, cy_ast.Union)):
            if node.members:
                found = []
                for field in node.members:
                    if isinstance(field, (cy_ast.Struct, cy_ast.Union)):
                        found.append(field)

                for nested in found:
                    # Create the necessary mangled names
                    mangled_name = '__fake_' + node.name + '_' + nested.name
                    mangled_typename = mangled_name + '_t'
                    
                    # Remove the nested definition from the node
                    node.members.remove(nested)

                    # Find the direct child of the toplevel ns
                    ns_child_node = node
                    while ns_child_node.context is not ns:
                        ns_child_node = ns_child_node.context

                    # now use that node to find the insertion idx
                    # in the toplevel namespace
                    insert_idx = ns.members.index(ns_child_node)

                    # Change the name of the nested struct to the mangled
                    # name and insert it into the namespace
                    nested.name = mangled_name
                    ns.members.insert(insert_idx, nested)

                    # Create a typedef for the new struct and insert
                    # it into the namespace just after the nested 
                    # item.
                    typedef = cy_ast.Typedef(mangled_typename, nested, ns)
                    typedef.location = ns_child_node.location
                    ns.members.insert(insert_idx + 1, typedef)
                    
                    # Find any fields that reference the
                    # nested struct, and replace the reference to that 
                    # of the typedef
                    for field in node.members:
                        if isinstance(field, cy_ast.Field):
                            if field.typ is nested:
                                field.typ = typedef
                    
                    # Finally, mark the the items as fake so they 
                    # won't later be rendered as extension types
                    typedef.fake = True
                    nested.fake = True


