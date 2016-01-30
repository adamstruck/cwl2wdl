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
from cwl2wdl.parsers import parse_cwl
from cwl2wdl.task import Task
from cwl2wdl.workflow import Workflow


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

    cwl = parse_cwl(arguments['FILE'])

    wdl_parts = []
    tasks = []
    worfklow = None

    if cwl['tasks'] is not None:
        for cwl_task in cwl['tasks']:
            tasks.append(Task(cwl_task))

        for task in tasks:
            wdl_task = WdlTaskGenerator(task)
            wdl_parts.append(wdl_task.generate_wdl())

    if cwl['workflow'] is not None:
        workflow = Workflow(cwl['workflow'])
        wdl_workflow = WdlWorkflowGenerator(workflow)
        wdl_parts.append(wdl_workflow.generate_wdl())

    wdl_doc = "\n".join(wdl_parts)
    print(wdl_doc)
