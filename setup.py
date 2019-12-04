from distutils.core import setup

setup(name='twittercrawler',
      version='0.1',
      description='Simple Twitter crawler based on Twython',
      url='',
      author='Ferenc Beres',
      author_email='fberes@info.ilab.sztaki.hu',
      packages=['twittercrawler'],
      install_requires=[
          'twython',
          'pymongo',
          'numpy',
          'datetime',
          'pandas',
          'networkx',
          'matplotlib',
          'bokeh',
          'pytest'
      ],
zip_safe=False)
