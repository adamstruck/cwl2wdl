#!/usr/bin/env python

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

import os
import re
import yaml
from docopt import docopt


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
            "array-File": "Array[File]+",
            "array-string": "Array[String]+",
            "array-int": "Array[Int]+",
            "array-long": "Array[Float]+",
            "array-float": "Array[Float]+",
            "array-double": "Array[Float]+"}


class WdlGenerator:
    def __init__(self, task_name, inputs, command, outputs, runtime):
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
        self.task_name = task_name
        self.inputs = inputs
        self.command = command
        self.outputs = outputs
        self.runtime = runtime
        self.wdl = None

    def format_inputs(self):
        inputs = []
        template = "{0} {1}"
        for var in self.inputs:
            inputs.append(template.format(var.variable_type,
                                          var.name))
        return "\n    ".join(inputs)

    def format_command(self):
        command_parts = [self.command.baseCommand]
        command_pos = [0]
        arg_template = "    {0} {1}"
        for arg in self.command.inputs:
            if arg.flag is None:
                flag = ""
            else:
                flag = arg.flag
            command_pos.append(arg.position)
            command_parts.append(arg_template.format(flag,
                                                     arg.name))

        cmd_order = [i[0] for i in sorted(enumerate(command_pos), key=lambda x: (x[1] is None, x[1]))]
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

    def generate(self):
        wdl = self.template % (self.task_name, self.format_inputs(),
                               self.format_command(), self.format_outputs(),
                               self.format_runtime())

        # if no relavant runtime variables are specified remove that
        # section from the template
        if self.format_runtime() == '':
            no_runtime = "\s+runtime {\s+}"
            wdl = re.sub(no_runtime, "", wdl)

        return wdl


class Task:
    def __init__(self, data):
        self.data = data
        self.baseCommand = data['baseCommand']
        self.inputs = data['inputs']
        self.outputs = data['outputs']
        self.requirements = data['requirements']

    def convert_inputs(self):
        wdl_inputs = []
        for field in self.inputs:
            wdl_inputs.append(Input(field))
        return wdl_inputs

    def convert_outputs(self):
        wdl_outputs = []
        for field in self.outputs:
            wdl_outputs.append(Output(field))
        return wdl_outputs

    def convert_requirements(self):
        wdl_runtime = []
        for field in self.requirements:
            # import addtional CWL definitions and update Task
            if '$import' in field:
                continue
            else:
                wdl_runtime.append(Requirement(field))
        return wdl_runtime

    def convert_command(self):
        return Command(self.baseCommand, self.convert_inputs())


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
        if cwl_input['type'].__class__ == str:
            self.variable_type = type_map[cwl_input['type']]
        else:
            cwl_type = "-".join([cwl_input['type']['type'],
                                 cwl_input['type']['items']])
            self.variable_type = type_map[cwl_type]


class Command:
    def __init__(self, baseCommand, inputs):
        self.baseCommand = " ".join(baseCommand)
        if all(isinstance(f, Input) == True for f in inputs):
            self.inputs = inputs
        else:
            raise TypeError("Command inputs must be of class 'Input'")


class Output:
    def __init__(self, cwl_output):
        # TODO: parse outputBinding
        self.output = cwl_output['outputBinding']
        self.name = cwl_output['id'].strip("#")
        # Types are remapped
        self.variable_type = type_map[cwl_output['type']]


class Requirement:
    def __init__(self, requirement):
        if 'class' in requirement:
            # check for docker spec
            if requirement['class'] == 'DockerRequirement':
                self.prefix = "docker"
                self.value = requirement['dockerImageId']
            # javascript is not supported in WDL
            elif requirement['class'] == 'InlineJavascriptRequirement':
                pass
        else:
            self.prefix = None
            self.value = None


def cwl2wdl():
    arguments = docopt(__doc__, version='0.1')

    handle = open(arguments['FILE'])
    data = yaml.load(handle.read())
    handle.close()

    task = Task(data)
    task_name = os.path.basename(arguments['FILE'])

    wdl_generator = WdlGenerator(
        task_name, task.convert_inputs(), task.convert_command(),
        task.convert_outputs(), task.convert_requirements())

    print(wdl_generator.generate())


if __name__ == "__main__":
    cwl2wdl()
