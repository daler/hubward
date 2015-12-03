from jsonschema import Draft4Validator, validators
import yaml
from collections import OrderedDict
from textwrap import wrap as _wrap


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Load YAML into an ordered dictionary to maintain key sorting.
    """
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def represent_odict(dump, tag, mapping, flow_style=None):
    """
    Dump an ordered dictionary to YAML, maintaining the key order but making it
    look like a normal dictionary (without the !!python/object extra stuff).

    From https://gist.github.com/miracle2k/3184458
    """
    value = []
    node = yaml.MappingNode(tag, value, flow_style=flow_style)
    if dump.alias_key is not None:
        dump.represented_objects[dump.alias_key] = node
    best_style = True
    if hasattr(mapping, 'items'):
        mapping = mapping.items()
    for item_key, item_value in mapping:
        node_key = dump.represent_data(item_key)
        node_value = dump.represent_data(item_value)
        if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style):
            best_style = False
        if not (isinstance(node_value, yaml.ScalarNode) and not node_value.style):
            best_style = False
        value.append((node_key, node_value))
    if flow_style is None:
        if dump.default_flow_style is not None:
            node.flow_style = dump.default_flow_style
        else:
            node.flow_style = best_style
    return node

yaml.SafeDumper.add_representer(OrderedDict,
    lambda dumper, value: represent_odict(dumper, u'tag:yaml.org,2002:map', value))



def access(dct, keys):
    """
    Access a value from an arbitrarily-nested dictionary, given a set of keys.

    If any key doesn't exist, returns None.


    >>> access({'a': {'aa': {'aaa': {'b': 1, 'c': 2}}}}, keys=['a', 'aa', 'aaa', 'b'])
    1
    """
    o = dct
    for k in keys:
        o = o.get(k)
        if o is None:
            return None
    return o


def follow_ref(ref, dct):
    """
    Follow a "$ref" JSON Schema reference
    """
    ref = ref.lstrip('#/')
    keys = ref.split('/')
    return access(dct, keys)


def _indent(s, amount):
    """
    Indents string `s` by `amount` doublespaces.
    """
    pad = '  ' * amount
    return '\n'.join([pad + i for i in s.splitlines(False)])


def create_config(schema, fout=None):
    """
    Generates an example config file based on the schema alone and writes it to
    `fout`, which can then be validated.

    The goal is to have the schema be the sole source of config files.

    "description" fields in the schema will be printed out as YAML comments,
    serving as documentation.

    Parameters
    ----------
    schema : str
        Filename of schema

    fout : file-like
        Output file to write YAML to.
    """

    d = ordered_load(open(schema), yaml.SafeLoader)

    def props(path, v, fout=None, print_key=True):
        """
        Recursively print out a filled-in config file based on the schema
        """

        # Set the full original and output file objects, but only on the first
        # time.
        try:
            props.orig
        except AttributeError:
            props.orig = v

        try:
            props.out
        except AttributeError:
            props.out = fout

        # Key into schema
        if path:
            k = path[-1]
        else:
            k = None

        def wrap(s):
            "wrap a string at the current indent level"
            return ("\n%s# " % (indent)).join(_wrap(s))

        indent = '  ' * props.level

        # Print out the description as a comment.
        if 'description' in v:
            props.out.write('\n%s# %s\n' % (indent, wrap(v['description'])))

        # Describe the possible values of any enums.
        if 'enum' in v:
            enum = '\n'.join(['%s# - "%s"' % (indent, i) for i in v['enum']])
            props.out.write(
                '{indent}# options for "{k}" are:\n{enum}\n'
                .format(**locals()))

        default = v.get('default')

        # Create an appropriate prefix. This avoids trailing spaces for keys
        # with no value; this also sets strings with no default to "" instead
        # of a blank space.
        prefix = " "
        if default is None:
            if v.get('type') == "string":
                default = '""'
            else:
                default = ""
                prefix = ""

        else:
            # It's tricky to get arrays to be generated using $ref references;
            # this allows a default to be written into the schema and printed
            # nicely in the generated output.

            if v.get('type') in ['object', 'array']:
                default ='\n' + _indent(
                    yaml.safe_dump(default, default_flow_style=False, indent=2, line_break=False),
                    props.level + 2
                )


        if not print_key:
            k = ""
            colon = ""
            indent = ""
        else:
            colon = ":"

        # Write out what we have so far.
        props.out.write(
            '{indent}{k}{colon}{prefix}{default}\n'.format(**locals()))


        # Follow references if needed for an array
        if 'type' in v and v['type'] == 'array':
            if 'default' not in v:
                props.level += 1
                props.out.write('%s-' % ('  ' * props.level))
                props.level -= 1

                if '$ref' in v['items']:
                    props.level += 1
                    props(path,
                          follow_ref(v['items']['$ref'],
                                     props.orig),
                          print_key=False)
                    props.level -= 1

        # Recursively call this function for everything in properties
        if 'properties' in v:
            for k, v in v['properties'].items():
                props.level += 1
                path.append(k)
                props(path, v)
                props.level -= 1
                path.pop()
        return

    # Set the default level and then recursively call props to generate the
    # YAML file.
    #
    props.level = -1
    props([], d, fout, print_key=False)
    return
