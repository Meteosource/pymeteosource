import os
from setuptools import find_packages, setup


with open(os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "README.md")) as f:
    README = f.read()

setup(
    version="0.0.1",
    name="pymeteosource",
    packages=find_packages(),
    install_requires=["wheel", "requests", "pytz"],
    extras_require={"pandas": "pandas"},
    description="Meteosource API wrapper library",
    long_description=README,
    author="Jan Dejdar",
    author_email="dejdar@meteocentrum.cz",
    url="https://www.meteosource.com/",
    license="???",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
