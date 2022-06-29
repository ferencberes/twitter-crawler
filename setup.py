from setuptools import find_packages, setup

install_requires=[
'twython',
'numpy',
'pandas',
'scipy',
'networkx',
'pymongo',
'matplotlib',
'bokeh',
'tqdm',
'comet_ml',
'kafka-python',
'tweepy',
'pyvis'
]

setup_requires = ['pytest-runner']

tests_require = [
#'codecov',
'pytest',
'pytest-cov',
]

setup(
  name='twittercrawler',
  packages = find_packages(),
  version='0.1.2',
  description='Simple Twitter crawler based on Twython',
  url='https://twittercrawler.readthedocs.io/en/latest/',
  author='Ferenc Beres',
  author_email='fberes@info.ilab.sztaki.hu',
  install_requires=install_requires,
  setup_requires=setup_requires,
  tests_require=tests_require,
)
