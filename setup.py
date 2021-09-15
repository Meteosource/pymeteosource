import os
from setuptools import find_packages, setup


with open(os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "README.md")) as f:
    README = f.read()

setup(
    version="0.1",
    name="pymeteosource",
    packages=find_packages(),
    install_requires=["wheel", "requests", "pytz"],
    extras_require={"pandas": "pandas"},
    description="Meteosource API wrapper library",
    long_description=README,
    author="Meteosource",
    author_email="support@meteosource.com",
    url="https://github.com/Meteosource/pymeteosource/archive/v_01.tar.gz",
    license="MIT",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
