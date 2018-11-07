from setuptools import setup, find_packages

setup(
    name="AWSIoTGG",
    version="0.3",
    packages=find_packages(),
    url="https://github.com/daviian/awsiotgg",

    install_requires=["AWSIoTPythonSDK>=1.3.1"],

    author="David Schneiderbauer",
    author_email="dschneiderbauer@gmail.com",
    description="Establishes AWS GreenGrass Connections"
)
