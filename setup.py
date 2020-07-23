from os.path import abspath, dirname, join
from setuptools import setup

# Read the README markdown data from README.md
with open(abspath(join(dirname(__file__), 'README.md')), 'rb') as readmeFile:
	__readme__ = readmeFile.read().decode('utf-8')

setup(
	name='ue4cli',
	version='0.0.46',
	description='Command-line interface for Unreal Engine 4',
	long_description=__readme__,
	long_description_content_type='text/markdown',
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Topic :: Software Development :: Build Tools',
		'Environment :: Console'
	],
	keywords='epic unreal engine',
	url='http://github.com/adamrehn/ue4cli',
	author='Adam Rehn',
	author_email='adam@adamrehn.com',
	license='MIT',
	packages=['ue4cli'],
	zip_safe=True,
	python_requires = '>=3.5',
	install_requires = [
		'setuptools>=38.6.0',
		'shellescape',
		'twine>=1.11.0',
		'wheel>=0.31.0'
	],
	entry_points = {
		'console_scripts': ['ue4=ue4cli.cli:main']
	}
)
