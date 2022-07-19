from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in tsxero/__init__.py
from tsxero import __version__ as version

setup(
	name="tsxero",
	version=version,
	description="Techseria Xero Integration with ERPNext",
	author="Techseria",
	author_email="support@techseria.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
