import argparse
import json


HEADER = \
"""/**********************************************************/
/*       AUTOGENERATED FILE, DO NOT EDIT BY HAND !        */
/*    Use tools/generate_bindings.py to regenerate it.    */
/**********************************************************/


#include "pythonscript.h"
#include "bindings/bindings.gen.h"


PYBIND11_PLUGIN(godot_bindings) {
    py::module m("godot.bindings", "Godot classes just for you ;-)");


"""
FOOTER = \
"""
    // Expose godot.bindings as a module
    auto sys = py::module::import("sys");
    sys.attr("modules")["godot.bindings"] = m;

    return m.ptr();
}
"""


def _comment_entry(item, entry):
    if item[entry]:
        return '// Bind %s' % entry
    else:
        return '// No %s to bind' % entry


def parse_item(item):
    output = []
    clsname = item['name']
    if item['base_class']:
        output.append('py::class_<{name}, {base_class}>(m, "{name}")'.format(**item))
    else:
        output.append('py::class_<{name}>(m, "{name}")'.format(**item))

    # TODO: is there Godot class that take constructor parameters ?
    output.append('.def(py::init<>())')

    if not item['instanciable']:
        # TODO: find a less clunky way to do this...
        output.append('.def("__new__", (py::object cls) -> { py::eval("raise TypeError(\'%s is not instanciable.\')"); })' % clsname)

    output.append(_comment_entry(item, 'methods'))
    for method in item['methods']:
        output.append('.def("{name}", &{clsname}::{name})'.format(clsname=clsname, **method))

    output.append(_comment_entry(item, 'constants'))
    for key, value in item['constants'].items():
        output.append('.def("{key}", {value})'.format(key=key, value=value))

    output.append(_comment_entry(item, 'properties'))
    for prop in item['properties']:
        output.append('.def_property("{name}", &{clsname}::{getter}, &{clsname}::{setter})'.format(clsname=clsname, **prop))

    # TODO: bind signals

    return '    ' + '\n        '.join(output)


def main(infd, outfd):
    api = json.load(infd)
    outfd.write(HEADER + '\n\n'.join([parse_item(x) for x in api]) + FOOTER)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=argparse.FileType('r'), help='Api json file')
    parser.add_argument('--output', '-o', type=argparse.FileType('w'), default='bindings.gen.cpp',
                        help='Generated output (default: bindings.gen.cpp)')
    args = parser.parse_args()
    main(args.input, args.output)