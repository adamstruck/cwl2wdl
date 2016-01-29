"""
Workflow descriptor classes
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from cwl2wdl.task import Input, Output, Requirement


class Workflow(object):
    def __init__(self, parsed_workflow):
        self.name = parsed_workflow['name']
        self.inputs = [Input(i) for i in parsed_workflow['inputs']]
        self.outputs = [Output(o) for o in parsed_workflow['outputs']]
        self.steps = [Step(s) for s in parsed_workflow['steps']]
        self.requirements = [Requirement(r) for r in parsed_workflow['requirements']]


class Step(object):
    def __init__(self, workflow_step):
        self.task_id = workflow_step['task_id']        
        self.task_definition = workflow_step['task_definition']
        self.import_statement = workflow_step['import_statement']
        self.inputs = [StepInput(i) for i in workflow_step['inputs']]
        self.outputs = [StepOutput(o) for o in workflow_step['outputs']]


class StepInput(object):
    def __init__(self, input_dict):
        self.input_id = input_dict['id']
        self.source = input_dict['source']


class StepOutput(object):
    def __init__(self, output_dict):
        self.output_id = output_dict['id']
