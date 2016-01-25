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

# Setup warning message format
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None:\
                         formatwarning_orig(message, category, filename,
                                            lineno, line='')


def remap_type(input_type):
    "Remaps CWL types to WDL types. Also determines if variable is optional."
    # Map Literals not currently supported
    # Key is CWL type
    # Value is corresponding WDL type
    type_map = {"File": "File",
                "string": "String",
                "boolean": "Boolean",
                "int": "Int",
                "long": "Float",
                "float": "Float",
                "double": "Float",
                "array-File": "Array[File]",
                "array-string": "Array[String]",
                "array-int": "Array[Int]",
                "array-long": "Array[Float]",
                "array-float": "Array[Float]",
                "array-double": "Array[Float]"}

    optional = False
    if input_type.__class__ == str:
        cwl_type = input_type

    elif input_type.__class__ == list:
        if 'null' in input_type:
            optional = True
            # keep the first non-null type
            cwl_type = [value for index, value in enumerate(input_type) if value != 'null'][0]
        if cwl_type.__class__ == dict:
            cwl_type = "-".join([cwl_type['type'],
                                 cwl_type['items']])

    elif input_type.__class__ == dict:
        cwl_type = "-".join([input_type['type'],
                             input_type['items']])

    optional = optional
    try:
        variable_type = type_map[cwl_type]
        return variable_type, optional
    except KeyError:
        raise KeyError('Unsupported type: %s' % (cwl_type))


class WdlWorkflowGenerator:
    def __init__(self, workflow):
        self.template = """
workflow %s {
    %s

    call %s {
        %s
    }
}
"""
        self.name = workflow.name
        self.inputs = workflow.inputs
        self.outputs = workflow.outputs
        self.steps = workflow.steps

    def format_inputs(self):
        inputs = []
        template = "{0} {1}"
        for var in self.inputs:
            if var.optional:
                variable_type = re.sub("($)", "?", var.variable_type)
            else:
                variable_type = var.variable_type
            inputs.append(template.format(variable_type,
                                          var.name))
        return "\n    ".join(inputs)

    def format_step(self):
        # TODO
        step_template = """
    call %s {
        %s
    }
"""
        steps = []
        for step in self.steps:
            steps.append(step_template % ())
        return "\n".join(steps)

    def generate_wdl(self):
        wdl = self.template % (self.name, self.format_inputs(),
                               self.format_steps())

        return wdl


class WdlTaskGenerator:
    def __init__(self, task):
        self.template = """
task %s {
    %s

    command {
        %s
    }

    output {
        %s
    }

    runtime {
        %s
    }
}
"""
        self.name = task.name
        self.inputs = task.inputs
        self.command = task.command
        self.outputs = task.outputs
        self.runtime = task.requirements

    def format_inputs(self):
        inputs = []
        template = "{0} {1}"
        for var in self.inputs:
            if var.optional:
                variable_type = re.sub("(\+$|$)", "?", var.variable_type)
            else:
                variable_type = var.variable_type
            inputs.append(template.format(variable_type,
                                          var.name))
        return "\n    ".join(inputs)

    def format_command(self):
        command_parts = [self.command.baseCommand]
        command_pos = [0]
        for arg in self.command.inputs:
            if arg.optional:
                arg_template = "    ${%s + %s}"
            else:
                arg_template = "    %s %s"

            if arg.flag is None:
                flag = ""
                arg_template = "    %s%s"
            else:
                flag = arg.flag

            command_pos.append(arg.position)
            command_parts.append(arg_template % (flag, arg.name))

        cmd_order = [i[0] for i in sorted(enumerate(command_pos),
                                          key=lambda x: (x[1] is None, x[1]))]
        ordered_command_parts = [command_parts[i] for i in cmd_order]

        return " \\\n        ".join(ordered_command_parts)

    def format_outputs(self):
        outputs = []
        template = "{0} {1} = {2}"
        for var in self.outputs:
            outputs.append(template.format(var.variable_type,
                                           var.name,
                                           var.output))
        return "\n        ".join(outputs)

    def format_runtime(self):
        template = "{0}: {1}"
        attributes = []
        for attribute in self.runtime:
            if vars(attribute) == {}:
                continue
            else:
                attributes.append(template.format(attribute.prefix,
                                                  attribute.value))
        return "\n        ".join(attributes)

    def generate_wdl(self):
        wdl = self.template % (self.name, self.format_inputs(),
                               self.format_command(), self.format_outputs(),
                               self.format_runtime())

        # if no relavant runtime variables are specified remove that
        # section from the template
        if self.format_runtime() == '':
            no_runtime = "\s+runtime {\s+}"
            wdl = re.sub(no_runtime, "", wdl)

        return wdl


class Task:
    def __init__(self, cwl):
        self.cwl_def = cwl
        self.name = cwl['label']
        self.command = Command(cwl['baseCommand'], cwl['inputs'])
        self.inputs = [Input(i) for i in cwl['inputs']]
        self.outputs = [Output(o) for o in cwl['outputs']]
        if 'requirements' in cwl:
            self.requirements = cwl['requirements']
        else:
            self.requirements = []

    def process_requirements(self):
        wdl_runtime = []
        for field in self.requirements:
            # import addtional CWL definitions and update Task
            if '$import' in field:
                continue
            else:
                wdl_runtime.append(Requirement(field))
        self.requirements = wdl_runtime


class Input:
    def __init__(self, cwl_input):
        self.name = cwl_input['id'].strip("#")

        if 'inputBinding' in cwl_input:
            if 'prefix' in cwl_input['inputBinding']:
                self.flag = cwl_input['inputBinding']['prefix']
            else:
                self.flag = None
            if 'position' in cwl_input['inputBinding']:
                self.position = cwl_input['inputBinding']['position']
            else:
                self.position = None
            if 'itemSeparator' in cwl_input['inputBinding']:
                self.separator = cwl_input['inputBinding']['itemSeparator']
            else:
                self.separator = None
        else:
            self.flag = None
            self.position = None
            self.separator = None

        if 'default' in cwl_input:
            self.default = cwl_input['default']
        else:
            self.default = None

        # Types need to be remapped
        self.variable_type, self.optional = remap_type(cwl_input['type'])


class Command:
    def __init__(self, baseCommand, inputs):
        if baseCommand.__class__ == list:
            self.baseCommand = " ".join(baseCommand)
        else:
            self.baseCommand = baseCommand
        self.inputs = [Input(i) for i in inputs]


class Output:
    def __init__(self, cwl_output):
        # TODO: parse outputBinding
        if 'outputBinding' in cwl_output:
            if 'glob' in cwl_output['outputBinding']:
                if cwl_output['outputBinding']['glob'].__class__ == str:
                    self.output = 'glob(\'%s\')' % (cwl_output['outputBinding']['glob'])
                else:
                    warnings.warn("Cannot evaluate expression within outputBinding.")
                    self.output = 'glob(\'%s\')' % (cwl_output['outputBinding']['glob'])
            else:
                warnings.warn("Unsupported outputBinding.")
                self.output = cwl_output['outputBinding']
        elif 'path' in cwl_output:
            self.output = cwl_output['path']
        else:
            self.output = None
        self.name = cwl_output['id'].strip("#")
        # Types must be remapped
        self.variable_type, self.optional = remap_type(cwl_output['type'])


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


class Workflow:
    def __init__(self, cwl_workflow):
        self.name = cwl_workflow['label']
        self.inputs = [Input(i) for i in cwl_workflow['inputs']]
        self.outputs = [Output(o) for o in cwl_workflow['outputs']]
        self.steps = cwl_workflow['steps']


class Step:
    def __init__(self, cwl_step):
        self.name = None
        self.inputs = None
        self.outputs = None


def cwl2wdl_main():
    arguments = docopt(__doc__, version='0.1')

    handle = open(arguments['FILE'])
    cwl = yaml.load(handle.read())
    handle.close()

    if cwl.__class__ == list:
        tasks = []
        for task in cwl:
            if task['class'] == 'CommandLineTool':
                if 'label' not in task:
                    task['label'] = "_".join(task['baseCommand'])
                task = Task(task)
                tasks.append(task)
            elif task['class'] == 'Workflow':
                if 'label' not in task:
                    task['label'] = re.sub("(.yaml|.cwl)", "",
                                           os.path.basename(arguments['FILE']))
                workflow = Workflow(task)
    else:
        if 'label' not in cwl:
            cwl['label'] = re.sub("(.yaml|.cwl)", "",
                                  os.path.basename(arguments['FILE']))
        tasks = [Task(cwl)]
        workflow = None

    wdl_parts = []
    for task in tasks:
        task.process_requirements()
        wdl_task = WdlTaskGenerator(task)

        wdl_parts.append(wdl_task.generate_wdl())

    # wdl_workflow = WdlWorkflowGenerator(workflow)
    # wdl_parts.append(wdl_workflow.generate_wdl())

    wdl_doc = "\n".join(wdl_parts)
    print(wdl_doc)
