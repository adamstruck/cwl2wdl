from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as readmeFile:
    long_description = readmeFile.read()

setup(
    name="cwl2wdl",
    description="Convert a CWL tool and workflow description to its WDL representation",
    long_description=long_description,
    packages=["cwl2wdl"],
    include_package_data=True,
    zip_safe=False,
    author="Adam Struck",
    author_email="strucka@ohsu.edu",
    url="https://github.com/adamstruck/cwl2wdl",    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    keywords='workflow tool',
    install_requires=["wdl==1.0.22"],
    entry_points={
        'console_scripts': [
            'cwl2wdl=cwl2wdl.main:cli'
        ]
    },
    # Use setuptools_scm to set the version number automatically from Git
    setup_requires=['setuptools_scm'],
    use_scm_version={
        "write_to": "cwl2wdl/_version.py"
    },
)
