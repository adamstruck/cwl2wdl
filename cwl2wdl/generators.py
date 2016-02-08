"""
Generator classes for WDL
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re


class WdlTaskGenerator(object):
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
        self.requirements = task.requirements
        self.stdin = task.stdin
        self.stdout = task.stdout

    def __format_inputs(self):
        inputs = []
        template = "%s %s"
        for var in self.inputs:
            if var.is_required:
                variable_type = var.variable_type
            else:
                variable_type = re.sub("($)", "?", var.variable_type)

            inputs.append(template % (variable_type,
                                      var.name))
        return "\n    ".join(inputs)

    def __format_command(self):
        command_position = [0]
        command_parts = [self.command.baseCommand]

        for arg in self.command.arguments:
            command_position.append(arg.position)

            if arg.prefix is not None:
                arg_template = "%s %s"
                prefix = arg.prefix
            else:
                arg_template = "%s%s"
                prefix = ""

            if arg.value is not None:
                value = arg.value
            else:
                value = ""

            formatted_arg = arg_template % (prefix, value)
            command_parts.append(formatted_arg)

        for command_input in self.command.inputs:
            # Some CWL inputs map be mapped to expressions
            # not quite sure how to handle these situations yet
            if command_input.variable_type == 'Boolean':
                if command_input.default == "False":
                    continue
                elif command_input.prefix is None:
                    continue
                else:
                    pass

            if command_input.name == self.stdout:
                continue

            # more standard cases
            if command_input.prefix is None:
                prefix = ""
                command_input_template = "%s${%s}"
            else:
                prefix = command_input.prefix
                if command_input.is_required:
                    command_input_template = "%s ${%s}"
                else:
                    command_input_template = "${%s + %s}"

            if command_input.variable_type.startswith("Array"):
                sep = "sep=\'%s\' " % (command_input.separator)
            else:
                sep = ""

            if command_input.default is not None:
                default = "default=\'%s\' " % (command_input.default)
            else:
                default = ""

            # prefix will be handled in the same way in the future
            # wdl4s and cromwell dont support this yet
            name = sep + default + command_input.name

            # store input postion if provided.
            # inputs come after the base command and arguments
            command_position.append(command_input.position)

            command_parts.append(
                command_input_template % (prefix, name)
            )

        cmd_order = [i[0] for i in sorted(enumerate(command_position),
                                          key=lambda x: (x[1] is None, x[1]))]
        ordered_command_parts = [command_parts[i] for i in cmd_order]

        for req in self.requirements:
            if req.requirement_type == "envVar":
                ordered_command_parts.insert(
                    0,
                    " ".join(["%s=\'%s\'" % (envvar[0], envvar[1]) for envvar in req.value])
                )

        # check if stdout is supposed to be captured to a file
        if self.stdout is not None:
            ordered_command_parts.append("> ${%s}" % (self.stdout))

        return " \\\n        ".join(ordered_command_parts)

    def __format_outputs(self):
        outputs = []
        template = "%s %s = %s"
        for var in self.outputs:
            outputs.append(template % (var.variable_type,
                                       var.name,
                                       var.output))
        return "\n        ".join(outputs)

    def __format_runtime(self):
        template = "%s: \'%s\'"
        requirements = []
        for requirement in self.requirements:
            if (requirement.requirement_type is None) or (requirement.value is None):
                continue
            else:
                requirements.append(template % (requirement.requirement_type,
                                                requirement.value))
        return "\n        ".join(requirements)

    def generate_wdl(self):
        wdl = self.template % (self.name, self.__format_inputs(),
                               self.__format_command(), self.__format_outputs(),
                               self.__format_runtime())

        # if no relavant runtime variables are specified remove that
        # section from the template
        if self.__format_runtime() == '':
            no_runtime = "\s+runtime {\s+}"
            wdl = re.sub(no_runtime, "", wdl)

        return wdl


class WdlWorkflowGenerator(object):
    def __init__(self, workflow):
        self.template = """
%s
workflow %s {
    %s
    %s
}
"""
        self.name = workflow.name
        self.inputs = workflow.inputs
        self.outputs = workflow.outputs
        self.steps = workflow.steps
        self.task_ids = []
        self.imported_tasks = []

    def __format_inputs(self):
        inputs = []
        template = "{0} {1}"
        for var in self.inputs:
            if var.is_required:
                variable_type = var.variable_type
            else:
                variable_type = re.sub("($)", "?", var.variable_type)

            inputs.append(template.format(variable_type,
                                          var.name))
        return "\n    ".join(inputs)

    def __format_steps(self):
        steps = []
        for step in self.steps:
            self.task_ids.append(step.task_id)

            if step.task_definition is not None:
                self.imported_tasks.append(
                    WdlTaskGenerator(step.task_definition).generate_wdl()
                )

            if step.inputs != []:
                step_template = """
    call %s {
        inputs: %s
    }
"""
                inputs = []
                for i in step.inputs:
                    inputs.append(
                        "%s = %s" % (re.sub(step.task_id + "\.", "", i.input_id),
                                     i.value)
                    )
                steps.append(step_template % (step.task_id,
                                              ", \n".join(inputs)))
            else:
                step_template = "call %s"
                steps.append(step_template % (step.task_id))
        return "\n".join(steps)

    def generate_wdl(self):
        wdl = self.template % ("\n".join(self.imported_tasks), self.name,
                               self.__format_inputs(), self.__format_steps())

        return wdl
