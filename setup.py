from setuptools import setup, find_packages

setup(
    name="AWSIoTGG",
    version="1.0",
    packages=find_packages(),
    url="https://github.com/daviian/awsiotgg",

    install_requires=["AWSIoTPythonSDK>=1.4.0"],

    author="David Schneiderbauer",
    author_email="dschneiderbauer@gmail.com",
    description="Establishes AWS GreenGrass Connections"
)
