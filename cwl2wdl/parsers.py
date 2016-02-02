"""
CWL parsers and helper functions
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import warnings
import yaml


class CwlParser(object):
    def __init__(self, sourceFile):
        self.sourceFile = sourceFile

    def parse_document(self):
        parentFileName = re.sub("(\.yaml)", "", os.path.basename(self.sourceFile))
        sourceDir = os.path.dirname(os.path.abspath(self.sourceFile))

        handle = open(self.sourceFile)
        cwl = yaml.load(handle.read())
        handle.close()

        if isinstance(cwl, list):
            tasks = [self.__parse_cwl_task(part, sourceDir) for part in cwl if part['class'] == 'CommandLineTool']
            workflow = [self.__parse_cwl_workflow(part, sourceDir, parentFileName) for part in cwl if part['class'] == 'Workflow'][0]

        elif isinstance(cwl, dict):
            if cwl['class'] == 'CommandLineTool':
                tasks = [self.__parse_cwl_task(cwl, sourceDir)]
                workflow = None
            elif cwl['class'] == 'Workflow':
                tasks = None
                workflow = self.__parse_cwl_workflow(cwl, sourceDir, parentFileName)
            else:
                raise TypeError("Unrecognized CWL class: %s" % (cwl['class']))
        else:
            raise TypeError("This doesn't appear to be a CWL document.")

        return {"tasks": tasks, "workflow": workflow}

    def __parse_cwl_task(self, cwl_task, sourceDir):
        if 'label' in cwl_task:
            name = re.sub("( |\.)", "_", cwl_task['label'])
        elif 'id' in cwl_task:
            name = re.sub("( |\.)", "_", cwl_task['id']).strip("#")
        else:
            name = "_".join(cwl_task['baseCommand'])

        name = self.__check_variable_value_for_reserved_syntax(name)

        if 'arguments' in cwl_task:
            arguments = self.__parse_cwl_arguments(cwl_task['arguments'])
        else:
            arguments = []

        baseCommand = cwl_task['baseCommand']
        inputs = self.__parse_cwl_inputs(cwl_task['inputs'])
        outputs = self.__parse_cwl_outputs(cwl_task['outputs'])

        if 'requirements' in cwl_task:
            requirements = self.__parse_cwl_requirements(cwl_task['requirements'], sourceDir)
        elif 'hints' in cwl_task:
            requirements = self.__parse_cwl_requirements(cwl_task['hints'], sourceDir)
        else:
            requirements = []

        if 'stdout' in cwl_task:
            if isinstance(cwl_task['stdout'], str):
                stdout = self.__check_variable_value_for_reserved_syntax(
                    re.sub("(inputs\.|^\$\(|\)$)", "", cwl_task['stdout'])
                )
            else:
                warnings.warn("Can't evaluate expression: %s in stdout" % (cwl_task['stdout']))
                stdout = str(cwl_task['stdout'])
        else:
            stdout = None

        if 'stdin' in cwl_task:
            if isinstance(cwl_task['stdin'], str):
                stdin = cwl_task['stdin']
            else:
                warnings.warn("Can't evaluate expression: %s in stdin" % (cwl_task['stdin']))
                stdin = str(cwl_task['stdin'])
        else:
            stdin = None

        return {"name": name, "baseCommand": baseCommand, "arguments": arguments,
                "inputs": inputs, "outputs": outputs, "requirements": requirements,
                "stdin": stdin, "stdout": stdout}

    def __parse_cwl_workflow(self, cwl_workflow, sourceDir, parentFileName):
        if 'label' in cwl_workflow:
            name = re.sub("( |\.)", "_", cwl_workflow['label'])
        elif 'id' in cwl_workflow:
            name = re.sub("( |\.)", "_", cwl_workflow['id']).strip("#")
        else:
            name = parentFileName

        name = self.__check_variable_value_for_reserved_syntax(name)

        inputs = self.__parse_cwl_inputs(cwl_workflow['inputs'])
        outputs = self.__parse_cwl_outputs(cwl_workflow['outputs'])
        steps = self.__parse_cwl_workflow_steps(cwl_workflow['steps'], sourceDir)

        if 'requirements' in cwl_workflow:
            requirements = self.__parse_cwl_requirements(cwl_workflow['requirements'], sourceDir)
        else:
            requirements = [{"requirement_type": None, "value": None}]

        return {"name": name, "inputs": inputs, "outputs": outputs,
                "steps": steps, "requirements": requirements}

    ############################
    # sub-section parsers
    ############################
    def __parse_cwl_command_line_binding(self, command_line_binding):
        if 'prefix' in command_line_binding:
            prefix = command_line_binding['prefix']
        else:
            prefix = None

        if 'position' in command_line_binding:
            position = command_line_binding['position']
        else:
            position = None

        if 'itemSeparator' in command_line_binding:
            separator = command_line_binding['itemSeparator']
        else:
            separator = None

        if 'valueFrom' in command_line_binding:
            value = command_line_binding['valueFrom']
        else:
            value = None

        return {"prefix": prefix,
                "position": position,
                "separator": separator,
                "value": value}

    def __parse_cwl_arguments(self, cwl_arguments):
        arguments = []
        if isinstance(cwl_arguments, list):
            for arg in cwl_arguments:
                if isinstance(arg, str):
                    arguments.append({'prefix': None, 'postion': None,
                                      'separator': None, 'value': arg})
                elif isinstance(arg, dict):
                    arguments.append(self.__parse_cwl_command_line_binding(arg))

        elif isinstance(cwl_arguments['arguments'], str):
            arguments.append({'prefix': None, 'postion': None,
                              'separator': None, 'value': cwl_arguments})

        elif isinstance(cwl_arguments['arguments'], dict):
            arguments.append(self.__parse_cwl_command_line_binding(cwl_arguments))

        return arguments

    def __parse_cwl_inputs(self, cwl_inputs):
        inputs = []
        for cwl_input in cwl_inputs:
            name = self.__check_variable_value_for_reserved_syntax(
                cwl_input['id'].strip("#")
            )
            is_required = self.__check_if_required(cwl_input['type'])
            variable_type = self.__remap_type_cwl2wdl(cwl_input['type'])

            if 'inputBinding' in cwl_input:
                inputBinding = self.__parse_cwl_command_line_binding(cwl_input['inputBinding'])
                prefix = inputBinding['prefix']
                position = inputBinding['position']
                separator = inputBinding['separator']
                value = inputBinding['value']
            else:
                prefix = None
                position = None
                separator = None
                value = None

            if variable_type.startswith("Array") and separator is None:
                separator = " "

            if 'default' in cwl_input:
                default = str(cwl_input['default'])
            elif value is not None:
                if isinstance(value, str):
                    default = value
                else:
                    warnings.warn("Expressions are not supported.")
                    default = str(value)
            else:
                default = None

            parsed_input = {"name": name, "variable_type": variable_type,
                            "is_required": is_required, "prefix": prefix,
                            "position": position, "separator": separator,
                            "default": default}
            inputs.append(parsed_input)
        return inputs

    def __parse_cwl_outputs(self, cwl_outputs):
        outputs = []
        for cwl_output in cwl_outputs:
            name = self.__check_variable_value_for_reserved_syntax(
                cwl_output['id'].strip("#")
            )
            is_required = self.__check_if_required(cwl_output['type'])
            variable_type = self.__remap_type_cwl2wdl(cwl_output['type'])

            if 'outputBinding' in cwl_output:
                if 'glob' in cwl_output['outputBinding']:
                    if isinstance(cwl_output['outputBinding']['glob'], str):
                        value = self.__check_variable_value_for_reserved_syntax(
                            re.sub("(inputs\.|^\$\(|\)$)", "", cwl_output['outputBinding']['glob'])
                        )
                        output = 'glob(\'${%s}\')' % (value)
                    else:
                        warnings.warn("Cannot evaluate expression within a 'glob' outputBinding.")
                        output = 'glob(\'${%s}\')' % (cwl_output['outputBinding']['glob'])
                else:
                    warnings.warn("Unsupported outputBinding: %s" % (cwl_output['outputBinding']))
                    output = cwl_output['outputBinding']

            else:
                warnings.warn("Not sure how to handle this output: %s" % (cwl_output))
                output = None

            parsed_output = {"name": name,
                             "variable_type": variable_type,
                             "is_required": is_required,
                             "output": output}
            outputs.append(parsed_output)
        return outputs

    def __parse_cwl_requirements(self, cwl_requirements, sourceDir=None):
        requirements = []
        for cwl_requirement in cwl_requirements:
            # check for docker requirement
            if 'class' in cwl_requirement:
                if cwl_requirement['class'] == 'DockerRequirement':
                    requirement_type = "docker"
                    if 'dockerImageId' in cwl_requirement:
                        value = cwl_requirement['dockerImageId']
                    elif 'dockerPull' in cwl_requirement:
                        value = cwl_requirement['dockerPull']
                    else:
                        req_type_err = [key for key in cwl_requirement.keys() if key.startswith("docker")]
                        warnings.warn(
                            "Unsupported docker requirement type: %s" % (" ".join(req_type_err)))
                        continue
                # inline javascript is not supported
                elif cwl_requirement['class'] == 'InlineJavascriptRequirement':
                    warnings.warn("This CWL file may contain InlineJavascript code."
                                  " WDL does not support this feature.")
                    continue
                else:
                    warnings.warn("The CWL requirement class: %s, is not supported" % (cwl_requirement['class']))
                    continue

            elif ('import' in cwl_requirement) or ('$import' in cwl_requirement):
                try:
                    to_import = cwl_requirement['import']
                except:
                    to_import = cwl_requirement['$import']

                if os.path.exists(to_import):
                    file_to_import = to_import
                elif os.path.exists(os.path.join(sourceDir, to_import)):
                    file_to_import = os.path.join(sourceDir, to_import)
                else:
                    warnings.warn("Couldn't find file: %s" % (to_import))
                    continue

                handle = open(file_to_import)
                imported_yaml = yaml.load(handle.read())
                handle.close()

                if isinstance(imported_yaml, list):
                    imported_requirements = self.__parse_cwl_requirements(imported_yaml)
                else:
                    imported_requirements = self.__parse_cwl_requirements([imported_yaml])

                requirements += imported_requirements
                continue
            else:
                warnings.warn("The CWL requirement: %s, is not supported" % (cwl_requirement))
                continue

            parsed_requirement = {"requirement_type": requirement_type,
                                  "value": value}
            requirements.append(parsed_requirement)

        return requirements

    def __parse_cwl_workflow_steps(self, workflow_steps, sourceDir):
        steps = []
        for step in workflow_steps:
            if 'import' in step['run']:
                task_id = re.sub('(\.cwl|#)', '', os.path.basename(step['run']['import']))
                if 'import' in step['run']['import'].endswith(".cwl"):
                    import_statement = "import " + step['run']['import']
                    to_import = step['run']['import']

            elif step['run'].endswith(".cwl"):
                task_id = re.sub('(\.cwl|#)', '', os.path.basename(step['run']))
                import_statement = "import " + step['run']
                to_import = step['run']

            else:
                task_id = re.sub('(\.cwl|#)', '', os.path.basename(step['run']))
                to_import = None
                import_statement = None
            
            if to_import is not None:
                if os.path.exists(to_import):
                    file_to_import = to_import
                elif os.path.exists(os.path.join(sourceDir, to_import)):
                    file_to_import = os.path.join(sourceDir, to_import)
                else:
                    raise IOError("Couldn't find file: %s" % (to_import))
                imported_cwl_task = CwlParser(file_to_import).parse_document()['tasks']
            else:
                imported_cwl_task = None

            inputs = []
            for step_input in step['inputs']:
                input_id = step_input['id'].strip('#')
                if 'source' in step_input:
                    value = step_input['source']
                elif 'default' in step_input:
                    value = step_input['default']
                else:
                    value = None

                if value is not None:
                    if isinstance(value, list):
                        value = " ".join([v.strip('#') for v in value])
                    else:
                        value = str(value).strip('#')

                inputs.append({'id': input_id, "value": value})

            outputs = []
            for o in step['outputs']:
                o['id'] = o['id'].strip('#')
                outputs.append(o)

            parsed_step = {"task_id": task_id,
                           "inputs": inputs,
                           "outputs": outputs,
                           "task_definition": imported_cwl_task,
                           "import_statement": import_statement}
            steps.append(parsed_step)
        return steps

    def __expression_converter(self, expression):
        # TODO
        pass

    ############################
    # Helper functions
    ############################
    def __check_variable_value_for_reserved_syntax(self, variable):
        wdl_reserved_words = ("call", "task", "workflow", "import", "input",
                              "output", "as", "if", "while", "runtime",
                              "scatter", "command", "parameter_meta", "meta",
                              "default", "sep", "prefix")
        if variable in wdl_reserved_words:
            return "_".join([variable, "variable"])
        else:
            return variable

    def __check_if_required(self, input_type):
        if isinstance(input_type, list):
            if 'null' in input_type:
                is_required = False
            else:
                is_required = True

        elif isinstance(input_type, dict):
            is_required = self.__check_if_required(input_type['type'])

        elif isinstance(input_type, str):
            if input_type == 'null':
                is_required = False
            else:
                is_required = True

        return is_required

    def __remap_type_cwl2wdl(self, input_type):
        "Remaps CWL types to WDL types. Also determines if variable is required."
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

        if isinstance(input_type, str):
            cwl_type = input_type

        elif isinstance(input_type, list):
            if 'null' in input_type:
                # select the non-null type
                cwl_type = [i for i in input_type if i != 'null'][0]

            if isinstance(cwl_type, dict):
                if cwl_type['type'] == "array":
                    cwl_type = "-".join([cwl_type['type'],
                                         cwl_type['items']])

                elif cwl_type['type'] == "enum":
                    raise KeyError('Unsupported CWL type: enum')

                elif cwl_type['type'] == "record":
                    raise KeyError('Unsupported CWL type: record')

        elif isinstance(input_type, dict):
            if input_type['type'] == "array":
                cwl_type = "-".join([input_type['type'],
                                     input_type['items']])

            elif input_type['type'] == "enum":
                raise KeyError('Unsupported CWL type: enum')

            elif input_type['type'] == "record":
                raise KeyError('Unsupported CWL type: record')

        try:
            variable_type = type_map[cwl_type]
            return variable_type
        except KeyError:
            raise KeyError('Unrecognized CWL type: %s' % (cwl_type))
