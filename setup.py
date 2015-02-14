from setuptools import find_packages, setup


with open('README.rst') as f:
    long_description = f.read()

setup(name='sr.comp.cli',
      version='1.0.0',
      packages=find_packages(),
      namespace_packages=['sr', 'sr.comp'],
      description='CLI tools for srcomp repositories',
      long_description=long_description,
      author='Student Robotics Competition Software SIG',
      author_email='srobo-devel@googlegroups.com',
      install_requires=[
          'sr.comp >=1.0, <2',
          'reportlab >=3.1.44, <4',
          'requests >=2.5.1, <3',
          'six >=1.9, <2'
      ],
      entry_points={
          'console_scripts': [
              'srcomp = sr.comp.cli.command_line:main'
          ]
      })
