# First, we try to use setuptools. If it's not available locally,
# we fall back on ez_setup.
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

with open("README.pypi.rst") as readmeFile:
    long_description = readmeFile.read()

setup(
    name="cwl2wdl",
    description="Convert CWL tool and workflow descriptions to WDL representations",
    license='MIT License',
    long_description=long_description,
    packages=["cwl2wdl"],
    include_package_data=True,
    zip_safe=False,
    author="Adam Struck",
    author_email="strucka@ohsu.edu",
    url="https://github.com/adamstruck/cwl2wdl",
    entry_points={
        'console_scripts': [
            'cwl2wdl=cwl2wdl.cwl2wdl:cwl2wdl'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    keywords='workflow tool',
    install_requires=[],
    # Use setuptools_scm to set the version number automatically from Git
    setup_requires=['setuptools_scm'],
    use_scm_version={
        "write_to": "_version.py"
    },
)
