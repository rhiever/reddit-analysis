import os
import re
from setuptools import setup

PACKAGE_NAME = 'redditanalysis'

INIT = open(os.path.join(os.path.dirname(__file__), PACKAGE_NAME,
                         '__init__.py')).read()
README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
VERSION = re.search("__version__ = '([^']+)'", INIT).group(1)

setup(name=PACKAGE_NAME,
      author='Randy Olson',
      author_email='rso@randalolson.com',
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      description=('A tool to aid in the production of word clouds for '
                   'subreddits and users on reddit.'),
      entry_points={'console_scripts': ['word_freqs={0}:main'
                                        .format(PACKAGE_NAME), ]},
      install_requires=['beautifulsoup', 'markdown', 'praw>=2.0.11',
                        'update_checker>=0.5'],
      license='GPLv3',
      long_description=README,
      packages=[PACKAGE_NAME],
      package_data={PACKAGE_NAME: ['words/*.txt']},
      test_suite='tests',
      url='https://github.com/rhiever/reddit-analysis',
      version=VERSION,
      zip_safe = False)
