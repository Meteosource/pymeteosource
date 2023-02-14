from pathlib import Path
from setuptools import find_packages, setup


setup(
    version="1.5.0",
    name="pymeteosource",
    packages=find_packages(),
    install_requires=["wheel", "requests", "pytz"],
    extras_require={"pandas": "pandas"},
    description="Meteosource API wrapper library",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type='text/markdown',
    author="Meteosource",
    author_email="support@meteosource.com",
    url="https://github.com/Meteosource/pymeteosource/archive/v1.5.0.tar.gz",
    license="MIT",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
