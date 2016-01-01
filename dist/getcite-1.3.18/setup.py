import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
	name = 'getcite',
	version = '1.3.18',
	description = 'Pulls original sources from Westlaw and HeinOnline.org',
	author = 'Samuel Alexander',
	author_email = 'salexander2000@gmail.com',
	license = 'GPL',
	packages = ['getcite'],
	
	install_requires = [
	'selenium>=2.48.0',
	'PyPDF2>=1.25'
	],

)
