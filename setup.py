from setuptools import setup, find_packages
import re
import os

__version__ = re.findall(
    r"""__version__ = ["']+([0-9\.]*)["']+""",
    open("polarbase/__init__.py").read(),
)[0]

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="polarbase",
    version=__version__,
    description="""polarBase is a simple Database to organize various polars""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="database polar",
    author="",
    author_email="",
    url="https://github.com/DavidAnderegg/polarbase",
    packages=find_packages(
        where='./',
        include=['polarbase*'],
        exclude=['tests']
        ),
    install_requires=[
    ],
    classifiers=[
        "Operating System :: Linux, Windows",
        "Programming Language :: Python",
        ],
)
