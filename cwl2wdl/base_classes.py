"""
Classes used to describe a tool or workflow
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class ParsedDocument(object):
    """Expects a parsed CWL document"""
    def __init__(self, parsed_doc):
        self.imports = None

        if (parsed_doc['tasks'] is None) and (parsed_doc['workflows'] is None):
            raise ImportError("Cannot convert NoneType to ParsedDocumentType.")

        if parsed_doc['tasks'] is not None:
            if isinstance(parsed_doc['tasks'], list):
                if all(isinstance(t, dict) for t in parsed_doc['tasks']):
                    self.tasks = [Task(t) for t in parsed_doc['tasks']]
                else:
                    raise TypeError
            else:
                raise TypeError
        else:
            self.tasks = None

        if parsed_doc['workflow'] is not None:
            if isinstance(parsed_doc['workflow'], dict):
                self.workflow = Workflow(parsed_doc['workflow'])
            else:
                raise TypeError
        else:
            self.workflow = None


class Task(object):
    def __init__(self, parsed_task):
        self.name = parsed_task['name']
        self.command = Command(parsed_task['baseCommand'],
                               parsed_task['arguments'],
                               parsed_task['inputs'])
        self.inputs = [Input(i) for i in parsed_task['inputs']]
        self.outputs = [Output(o) for o in parsed_task['outputs']]
        self.requirements = [Requirement(r) for r in parsed_task['requirements']]
        self.stdin = parsed_task['stdin']
        self.stdout = parsed_task['stdout']


class Input(object):
    def __init__(self, input_dict):
        self.name = input_dict['name']
        self.prefix = input_dict['prefix']
        self.position = input_dict['position']
        self.separator = input_dict['separator']
        self.default = input_dict['default']
        self.variable_type = input_dict['variable_type']
        self.is_required = input_dict['is_required']
        self.separate = input_dict.get("separate", True)


class Command(object):
    def __init__(self, baseCommand, arguments, inputs):
        if isinstance(baseCommand, list):
            self.baseCommand = " ".join(baseCommand)
        else:
            self.baseCommand = baseCommand

        self.arguments = [Argument(a) for a in arguments]
        self.inputs = [Input(i) for i in inputs]


class Argument(object):
    def __init__(self, argument_dict):
        self.prefix = argument_dict['prefix']
        self.position = argument_dict['position']
        self.value = argument_dict['value']


class Output(object):
    def __init__(self, output_dict):
        self.name = output_dict['name']
        self.output = output_dict['output']
        self.variable_type = output_dict['variable_type']
        self.is_required = output_dict['is_required']


class Requirement(object):
    def __init__(self, cwl_requirement):
        self.requirement_type = cwl_requirement['requirement_type']
        self.value = cwl_requirement['value']


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
        self.task_definition = Task(workflow_step['task_definition']) if workflow_step['task_definition'] is not None else None
        self.import_statement = workflow_step['import_statement']
        self.inputs = [StepInput(i) for i in workflow_step['inputs']]
        self.outputs = [StepOutput(o) for o in workflow_step['outputs']]


class StepInput(object):
    def __init__(self, input_dict):
        self.input_id = input_dict['id']
        self.value = input_dict['value']


class StepOutput(object):
    def __init__(self, output_dict):
        self.output_id = output_dict['id']
