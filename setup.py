from setuptools import setup, find_packages

setup(
	name="AWSIoTGG",
	version="0.1",
	packages=find_packages(),
	url="https://code.dschneiderbauer.me/tu-wien-dsg/awsiotgg",

	install_requires=["requests>=2.18"],

	author="David Schneiderbauer",
	author_email="dschneiderbauer@gmail.com",
	description="Performs AWS GreenGrass Discovery and Connection Establishment"
)
