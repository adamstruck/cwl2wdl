#!/usr/bin/env cwl-runner
#
# Author: Andrey.Kartashov@cchmc.org (http://orcid.org/0000-0001-9102-5681) / Dr. Barski Lab / Cincinnati Children’s Hospital Medical Center
# Developed for CWL consortium http://commonwl.org/

class: Workflow

cwlVersion: "cwl:draft-3.dev3"

description:
  creates genome coverage bigWig file from .bam file

requirements:
  - $import: ../../tools/envvar-global.cwl

inputs:
  - id: input
    type: File

  - id: genomeFile
    type: File

  - id: scale
    type: float

  - id: pairchip
    type: ["null",boolean]

  - id: fragmentsize
    type: ["null",int]

  - id: strand
    type: ["null",string]

  - id: bigWig
    type: string

outputs:
  - id: outfile
    type: File
    source: "#bigwig/bigWigOut"

steps:
  - id: genomecov
    run: ../../tools/bedtools-genomecov.cwl
    inputs:
      - {id: input, source: "#input"}
      - {id: genomeFile, source: "#genomeFile"}
      - {id: genomecoverageout, default: "genomecov.bed" }
      - {id: dept, default: '-bg' }
      - {id: split, default: true }
      - {id: pairchip, source: "#pairchip" }
      - {id: fragmentsize, source: "#fragmentsize" }
      - {id: scale, source: "#scale" }
      - {id: strand, source: "#strand" }
    outputs:
      - {id: genomecoverage}

  - id: sort
    run: ../../tools/linux-sort.cwl
    inputs:
      - {id: input, source: "#genomecov/genomecoverage" }
      - {id: key", default: ["1,1","2,2n"] }
    outputs:
      - {id: sorted}

  - id: bigwig
    run: ../../tools/ucsc-bedGraphToBigWig.cwl
    inputs:
      - {id: input, source: "#sort/sorted"}
      - {id: genomeFile, source: "#genomeFile"}
      - {id: bigWig, source: "#bigWig"}
    outputs:
      - {id: bigWigOut}
