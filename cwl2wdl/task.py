"""
Classes used to describe a tool
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class Task:
    def __init__(self, description):
        self.name = description['name']
        self.description = description['description']
        self.command = Command(description['baseCommand'], description['inputs'])
        self.inputs = [Input(i) for i in description['inputs']]
        self.outputs = [Output(o) for o in description['outputs']]
        self.requirements = [Requirement(r) for r in description['requirements']]


class Input:
    def __init__(self, input_dict):
        self.name = input_dict['name']
        self.flag = input_dict['flag']
        self.position = input_dict['position']
        self.separator = input_dict['separator']
        self.default = input_dict['default']
        self.variable_type = input_dict['variable_type']
        self.is_required = input_dict['is_required']


class Command:
    def __init__(self, baseCommand, inputs):
        if baseCommand.__class__ == list:
            self.baseCommand = " ".join(baseCommand)
        else:
            self.baseCommand = baseCommand
        self.inputs = [Input(i) for i in inputs]


class Output:
    def __init__(self, output_dict):
        self.name = output_dict['name']
        self.output = output_dict['output']
        self.variable_type = output_dict['variable_type']
        self.is_required = output_dict['is_required']


class Requirement:
    def __init__(self, cwl_requirement):
        if 'class' in cwl_requirement:
            # check for docker spec
            if cwl_requirement['class'] == 'DockerRequirement':
                self.prefix = "docker"
                self.value = cwl_requirement['dockerImageId']
            # javascript is not supported in WDL
            elif cwl_requirement['class'] == 'InlineJavascriptRequirement':
                warnings.warn("This CWL file contains Javascript code."
                              " WDL does not support this feature.")
        else:
            self.prefix = None
            self.value = None
