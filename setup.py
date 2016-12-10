import os
import re
from setuptools import setup

PACKAGE_NAME = "redditanalysis"

INIT = open(os.path.join(os.path.dirname(__file__), PACKAGE_NAME, "__init__.py")).read()
VERSION = re.search("__version__ = \"([^\"]+)\"", INIT).group(1)

def get_long_description():
    readme_file = "README.md"
    if not os.path.isfile(readme_file):
        return ""
    # Try to transform the README from Markdown to reStructuredText.
    try:
        os.system("pandoc --from=markdown --to=rst --output=README.rst README.md")
        description = open("README.rst").read()
        os.remove("README.rst")
    except Exception:
        description = open(readme_file).read()
    return description


setup(name=PACKAGE_NAME,
      author="Randal S. Olson",
      author_email="rso@randalolson.com",
      classifiers=["Intended Audience :: Developers",
                   "Intended Audience :: Science/Research",
                   "License :: OSI Approved :: BSD License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Topic :: Internet"],
      description=("A tool to aid in the production of word clouds for "
                   "subreddits and users on reddit."),
      entry_points={"console_scripts": ["word_freqs={0}:main".format(PACKAGE_NAME), ]},
      install_requires=["beautifulsoup4", "markdown", "praw >=2.1, <4", "update_checker==0.11", "lxml"],
      license="GPLv3",
      long_description=get_long_description(),
      packages=[PACKAGE_NAME],
      package_data={PACKAGE_NAME: ["words/*.txt"]},
      test_suite="tests",
      url="https://github.com/rhiever/reddit-analysis",
      version=VERSION,
      zip_safe=False)
