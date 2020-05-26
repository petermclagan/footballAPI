from setuptools import setup, find_packages

with open('requirements.txt') as r:
	requirements = r.readlines()

setup(
	name='betfair-historical',
	version='0.1.0',
	description='www.api-football.com tooling',
	author='Peter McLagan',
	author_email='peter.mclagan94@gmail.com',
	url='https://github.com/petermclagan/footballAPI',
	packages=find_packages(),
	install_requires=requirements,
	license='MIT',
	zip_safe=False
	)