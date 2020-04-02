import os
import argparse

from opencmiss.zinc.context import Context
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node
from opencmiss.utils.zinc.field import findOrCreateFieldFiniteElement


class ProgramArguments(object):
    pass


def addPressureField(field, nodeset='nodes'):
    fm = field.getFieldmodule()
    fm.beginChange()
    cache = fm.createFieldcache()
    if nodeset == 'nodes':
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    else:
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
    pressureField = findOrCreateFieldFiniteElement(fm, name='pressure', components_count=1, type_coordinate=False)
    pressureNodetemplate = nodes.createNodetemplate()

    node_iter = nodes.createNodeiterator()
    node = node_iter.next()

    while node.isValid():
        pressureNodetemplate.defineFieldFromNode(pressureField, node)
        # node.merge(pressureNodetemplate)
        cache.setNode(node)
        pressureField.setNodeParameters(cache, -1, Node.VALUE_LABEL_VALUE, 1, 1000)
        node = node_iter.next()
    fm.endChange()


class AddExtraField(object):

    def __init__(self, filename, output_filename):
        self._context = Context("AddField")
        self._region = self._context.getDefaultRegion()
        self._region.readFile(filename)

        self._output_file = output_filename

        self._add_field()

    def _get_mesh(self):
        fm = self._region.getFieldmodule()
        for dimension in range(3, 0, -1):
            mesh = fm.findMeshByDimension(dimension)
            if mesh.getSize() > 0:
                return mesh
        raise ValueError('Model contains no mesh')

    def _add_field(self):
        fm = self._region.getFieldmodule()
        addPressureField(fm.findFieldByName("pressure"),
                          nodeset='nodes')

        self._write()

    def _write(self):
        self._region.writeFile(self._output_file)


def main():
    args = parse_args()
    if os.path.exists(args.input_ex):
        if args.output_ex is None:
            filename = os.path.basename(args.input_ex)
            dirname = os.path.dirname(args.input_ex)
            output_ex = os.path.join(dirname, filename.split('.')[0] + '_test.' + filename.split('.')[1])
        else:
            output_ex = args.output_ex

    teg = AddExtraField(args.input_ex, output_ex)
    # teg.add_field()


def parse_args():
    parser = argparse.ArgumentParser(description="Transform (currently only scale) EX data.")
    parser.add_argument("input_ex", help="Location of the input EX file.")
    parser.add_argument("-o", "--output-ex", help="Location of the output ex file. "
                                            "[defaults to the location of the input file if not set.]")

    program_arguments = ProgramArguments()
    parser.parse_args(namespace=program_arguments)

    return program_arguments


if __name__ == "__main__":
    main()
