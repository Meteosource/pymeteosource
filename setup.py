from setuptools import find_packages, setup


setup(
    version="0.1",
    name="pymeteosource",
    packages=find_packages(),
    install_requires=["wheel", "requests", "pytz"],
    extras_require={"pandas": "pandas"},
    description="Meteosource API wrapper library",
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
