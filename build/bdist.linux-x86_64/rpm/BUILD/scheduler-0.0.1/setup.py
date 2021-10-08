from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


requirements = [i.strip() for i in open("requirements.txt").readlines()]

setup(name='scheduler',
      version='0.0.1',
      description='Hardware Test and Inventory Automation API',
      long_description=long_description,
      license="Source Code Corporation",
      platforms=["linux"],
      entry_points={
          'console_scripts': [
              'scheduler = scheduler.app:main',
          ]
      },
      keywords='scheduler, hardware',
      packages=find_packages(exclude=["tests*", "docs*", "hardware*"], ),
      install_requires=requirements,
      setup_requires=['wheel']
      )
