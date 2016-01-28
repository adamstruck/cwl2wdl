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

import warnings
import yaml

from docopt import docopt

from generators import WdlTaskGenerator
from parsers import CwlParser, CwlTaskParser
from task import Task


# Setup warning message format
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None:\
                         formatwarning_orig(message, category, filename,
                                            lineno, line='')


def cwl2wdl_main():
    arguments = docopt(__doc__, version='0.1')

    handle = open(arguments['FILE'])
    cwl_yaml = yaml.load(handle.read())
    handle.close()

    cwl = CwlParser(cwl_yaml, arguments['FILE'])
    tasks = []
    for cwl_task in cwl.tasks:
        tasks.append(Task(CwlTaskParser(cwl_task, arguments['FILE'])))

    wdl_parts = []
    for task in tasks:
        wdl_task = WdlTaskGenerator(task)
        wdl_parts.append(wdl_task.generate_wdl())

    wdl_doc = "\n".join(wdl_parts)
    print(wdl_doc)
