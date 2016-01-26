"""
Workflow descriptor classes
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from cwl2wdl import task


class Workflow:
    def __init__(self, parsed_workflow_instance):
        self.name = parsed_workflow_instance['label']
        self.inputs = [task.Input(i) for i in parsed_workflow_instance['inputs']]
        self.outputs = [task.Output(o) for o in parsed_workflow_instance['outputs']]
        self.steps = parsed_workflow_instance['steps']


class Step:
    def __init__(self, workflow_step):
        self.name = None
        self.inputs = None
        self.outputs = None
