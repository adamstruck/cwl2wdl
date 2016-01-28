"""
Workflow descriptor classes
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from task import Input, Output, Requirement


class Workflow(object):
    def __init__(self, workflow_parser_instance):
        self.name = workflow_parser_instance['label']
        self.inputs = [Input(i) for i in workflow_parser_instance['inputs']]
        self.outputs = [Output(o) for o in workflow_parser_instance['outputs']]
        self.steps = [Step(s) for s in workflow_parser_instance['steps']]
        self.requirements = [Requirement(r) for r in workflow_parser_instance['requirements']]


class Step(object):
    def __init__(self, workflow_step):
        self.task_id = workflow_step['task_id']
        self.inputs = [StepInput(i) for i in workflow_step['inputs']]
        self.outputs = [StepOutput(o) for o in workflow_step['outputs']]


class StepInput(object):
    def __init__(self, input_dict):
        self.input_id = input_dict['id']
        self.source = input_dict['source']


class StepOutput(object):
    def __init__(self, output_dict):
        self.output_id = output_dict['id']
