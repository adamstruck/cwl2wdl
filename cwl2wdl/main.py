"""
Convert a CWL task definition into a WDL representation.

Usage:
    cwl2wdl FILE
    cwl2wdl (-h | --help)
    cwl2wdl --version

Arguments:
    FILE       CWL input file

Options:
    -h --help
    --version  Show version.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import warnings

from docopt import docopt

import cwl2wdl
from cwl2wdl.generators import WdlTaskGenerator, WdlWorkflowGenerator
from cwl2wdl.parsers import CwlParser
from cwl2wdl.base_classes import ParsedDocument


# Setup warning message format
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None:\
                         formatwarning_orig(message, category, filename,
                                            lineno, line='')


def cli():
    arguments = docopt(__doc__, version=str(cwl2wdl.__version__))

    if os.path.exists(arguments['FILE']):
        pass
    else:
        raise IOError("%s does not exist." % (arguments['FILE']))

    parsed_cwl = ParsedDocument(
        CwlParser(arguments['FILE']).parse_document()
    )

    wdl_parts = []
    if parsed_cwl.tasks is not None:
        for task in parsed_cwl.tasks:
            wdl_task = WdlTaskGenerator(task).generate_wdl()
            wdl_parts.append(wdl_task)

    if parsed_cwl.workflow is not None:
        wdl_workflow = WdlWorkflowGenerator(parsed_cwl.workflow).generate_wdl()
        wdl_parts.append(wdl_workflow)

    wdl_doc = "\n".join(wdl_parts)
    print(wdl_doc)
