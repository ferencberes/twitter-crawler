from distutils.core import setup

setup(name='twittercrawler',
      version='0.1',
      description='Simple Twitter crawler based on Twython',
      url='',
      author='Ferenc Beres',
      author_email='fberes@info.ilab.sztaki.hu',
      packages=['twittercrawler','twittercrawler.replies'],
      install_requires=[
          'twython',
          'numpy',
          'pandas',
          'scipy',
          'networkx',
          'pymongo',
          'matplotlib',
          'bokeh',
          'pytest'
      ],
zip_safe=False)
