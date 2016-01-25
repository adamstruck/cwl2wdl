"""
Workflow descriptor classes
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from cwl2wdl import task


class Workflow:
    def __init__(self, cwl_workflow):
        self.name = cwl_workflow['label']
        self.inputs = [task.Input(i) for i in cwl_workflow['inputs']]
        self.outputs = [task.Output(o) for o in cwl_workflow['outputs']]
        self.steps = cwl_workflow['steps']


class Step:
    def __init__(self, cwl_step):
        self.name = None
        self.inputs = None
        self.outputs = None
