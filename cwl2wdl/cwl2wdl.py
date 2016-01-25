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
import re
import warnings
import yaml

from docopt import docopt

from cwl2wdl import generator
from cwl2wdl import parser
from cwl2wdl import task
from cwl2wdl import workflow


# Setup warning message format
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None:\
                         formatwarning_orig(message, category, filename,
                                            lineno, line='')


def cwl2wdl_main():
    arguments = docopt(__doc__, version='0.1')

    handle = open(arguments['FILE'])
    cwl = yaml.load(handle.read())
    handle.close()

    if cwl.__class__ == list:
        tasks = []
        for field in cwl:
            if task['class'] == 'CommandLineTool':
                if 'label' not in task:
                    task['label'] = "_".join(task['baseCommand'])
                task = task.Task(task)
                tasks.append(task)
            elif task['class'] == 'Workflow':
                if 'label' not in task:
                    task['label'] = re.sub("(.yaml|.cwl)", "",
                                           os.path.basename(arguments['FILE']))
                wdl_workflow = workflow.Workflow(task)
    else:
        if 'label' not in cwl:
            cwl['label'] = re.sub("(.yaml|.cwl)", "",
                                  os.path.basename(arguments['FILE']))
        tasks = [task.Task(cwl)]
        wdl_workflow = None

    wdl_parts = []
    for task in tasks:
        task.process_requirements()
        wdl_task = generator.WdlTaskGenerator(task)

        wdl_parts.append(wdl_task.generate_wdl())

    wdl_workflow_obj = WdlWorkflowGenerator(wdl_workflow)
    wdl_parts.append(wdl_workflow_obj.generate_wdl())

    wdl_doc = "\n".join(wdl_parts)
    print(wdl_doc)
