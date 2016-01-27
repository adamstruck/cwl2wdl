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
        self.runtime = task.requirements

    def format_inputs(self):
        inputs = []
        template = "%s %s"
        for var in self.inputs:
            if var.is_required:
                variable_type = re.sub("(\+$|$)", "?", var.variable_type)
            else:
                variable_type = var.variable_type
            inputs.append(template % (variable_type,
                                      var.name))
        return "\n    ".join(inputs)

    def format_command(self):
        command_parts = [self.command.baseCommand]
        command_pos = [0]
        for arg in self.command.inputs:
            if arg.is_required:
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
        template = "%s %s = %s"
        for var in self.outputs:
            outputs.append(template % (var.variable_type,
                                       var.name,
                                       var.output))
        return "\n        ".join(outputs)

    def format_runtime(self):
        template = "%s: %s"
        requirements = []
        for requirement in self.runtime:
            if (requirement.requirement_type is None) or (requirement.value is None):
                continue
            else:
                requirements.append(template % (requirement.requirement_type,
                                                requirement.value))
        return "\n        ".join(requirements)

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


class WdlWorkflowGenerator(object):
    def __init__(self, workflow):
        self.template = """
workflow %s {
    %s

    %s
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
            if var.is_required:
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
