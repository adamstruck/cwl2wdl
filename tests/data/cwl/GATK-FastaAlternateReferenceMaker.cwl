#!/usr/bin/env cwl-runner

cwlVersion: "cwl:draft-3.dev3"

class: CommandLineTool

description: |
  GATK-FastaAlternateReferenceMaker.cwl is developed for CWL consortium

requirements:
- $import: envvar-global.cwl
- $import: GATK-docker.cwl
- class: InlineJavascriptRequirement

inputs:
- id: "reference"
  type: File
  description: |
    Input reference fasta or fasta.gz
  inputBinding:
    prefix: "-R"
    position: 4

- id: "vcf"
  type: File
  description: |
    Input VCF file
    Variants from this VCF file are used by this tool as input. The file must at least contain the standard VCF header lines, but can be empty (i.e., no variants are contained in the file).
    --variant binds reference ordered data. This argument supports ROD files of the following types: BCF2, VCF, VCF3
  inputBinding:
    prefix: "-V"
    position: 4

- id: "intervals"
  type:
    - "null"
    - File
  inputBinding:
    prefix: "-L"
    position: 4

- id: "snpmask"
  type:
  - "null"
  - File
  description: |
    SNP mask VCF file
  inputBinding:
    prefix: "--snpmask"
    position: 4

- id: "output_filename"
  type: string
  inputBinding:
    prefix: "-o"
    position: 4

outputs:
- id: "#output"
  type: File
  description: >
    An output file created by the walker. Will overwrite contents if file exists
  outputBinding:
    glob: $(inputs.output_filename)

baseCommand: ["java"]

arguments:
- valueFrom: "-Xmx4g"
  position: 1
- valueFrom: "/usr/local/bin/GenomeAnalysisTK.jar"
  position: 2
  prefix: "-jar"
- valueFrom: "FastaAlternateReferenceMaker"
  position: 3
  prefix: "-T"


$namespaces:
  dct: http://purl.org/dc/terms/
  foaf: http://xmlns.com/foaf/0.1/
  doap: http://usefulinc.com/ns/doap#
  adms: http://www.w3.org/ns/adms#
  dcat: http://www.w3.org/ns/dcat#
  schema: http://schema.org/

$schemas:
- https://sparql-test.commonwl.org/schema.rdf
- http://dublincore.org/2012/06/14/dcterms.rdf
- http://xmlns.com/foaf/spec/20140114.rdf
- http://usefulinc.com/ns/doap#
- http://www.w3.org/ns/adms#
- http://www.w3.org/ns/dcat.rdf

schema:mainEntity:
  $import: https://scidap.com/description/tools/GATK.yaml

schema:downloadUrl: https://github.com/common-workflow-language/workflows/blob/master/tools/GATK-FastaAlternateReferenceMaker.cwl
schema:codeRepository: https://github.com/common-workflow-language/workflows
schema:license: http://www.apache.org/licenses/LICENSE-2.0
schema:isPartOf:
  class: schema:CreativeWork
  schema:name: "Common Workflow Language"
  schema:url: http://commonwl.org/

schema:author:
  $import: https://scidap.com/description/porter.yaml

