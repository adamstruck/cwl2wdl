"""
Convert a CWL task definition into a WDL representation.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import warnings

import argparse
import wdl.parser

import cwl2wdl
from cwl2wdl.generators import WdlTaskGenerator, WdlWorkflowGenerator
from cwl2wdl.parsers import CwlParser
from cwl2wdl.base_classes import ParsedDocument


# Setup warning message format
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None:\
                         formatwarning_orig(message, category, filename,
                                            lineno, line='')


def collect_args():
    parser = argparse.ArgumentParser(
        prog="cwl2wdl",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser._optionals.title = "Options"
    parser.add_argument("FILE", type=str, help="CWL file.")
    parser.add_argument("-f", "--format", type=str, default="wdl",
                        choices=["wdl", "ast"],
                        help="specify the output format")
    parser.add_argument("--validate", action="store_true",
                        help="validate the resulting WDL code with PyWDL")
    parser.add_argument("--version", action='version',
                        version=str(cwl2wdl.__version__))
    return parser


class ValidationError(Exception):
    pass


def cli():
    parser = collect_args()
    arguments = parser.parse_args()

    if os.path.exists(arguments.FILE):
        pass
    else:
        raise IOError("%s does not exist." % (arguments.FILE))

    parsed_cwl = ParsedDocument(
        CwlParser(arguments.FILE).parse_document()
    )

    wdl_parts = []
    if parsed_cwl.tasks is not None:
        for task in parsed_cwl.tasks:
            wdl_task = WdlTaskGenerator(task).generate_wdl()
            wdl_parts.append(wdl_task)

    if parsed_cwl.workflow is not None:
        wdl_workflow = WdlWorkflowGenerator(parsed_cwl.workflow).generate_wdl()
        wdl_parts.append(wdl_workflow)

    wdl_doc = str("\n".join(wdl_parts))

    if arguments.validate:
        try:
            is_validated = wdl.parser.parse(wdl_doc)
        except Exception as e:
            raise e

    if arguments.format == "ast":
        warnings.warn("By specifying 'ast' format you are implicity imposing validation.")
        ast = wdl.parser.parse(wdl_doc).ast()
        print(ast.dumps(indent=2))
    else:
        print(wdl_doc)
