from setuptools import setup

setup(name='SkypeLog',
      version='0.0.1',
      description='Skype log reader',
      url='http://github.com/takumaw/skype-log-for-python',
      author='WATANABE Takuma',
      author_email='takumaw@sfo.kuramae.ne.jp',
      license='GPL v2',
      packages=['SkypeLog', 'SkypeLog/locales'],
      scripts=['bin/skypelogconv'],
      zip_safe=False)

