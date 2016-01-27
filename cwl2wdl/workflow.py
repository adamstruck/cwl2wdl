"""
Workflow descriptor classes
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from task import Input, Output, Requirement


class Workflow(object):
    def __init__(self, parsed_workflow_instance):
        self.name = parsed_workflow_instance['label']
        self.inputs = [Input(i) for i in parsed_workflow_instance['inputs']]
        self.outputs = [Output(o) for o in parsed_workflow_instance['outputs']]
        self.steps = [Step(s) for s in parsed_workflow_instance['steps']]
        self.requirements = [Requirement(r) for r in parsed_workflow_instance['requirements']]


class Step(object):
    def __init__(self, workflow_step):
        self.name = workflow_step['task_id']
        self.inputs = [Input(i) for i in workflow_step['inputs']]
        self.outputs = [Output(o) for o in workflow_step['outputs']]
