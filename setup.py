from setuptools import setup

setup(name='SkypeLogClassic',
      version='0.0.1',
      description='Skype log reader (classic)',
      url='http://github.com/takumaw/skype-log-for-python',
      author='WATANABE Takuma',
      author_email='takumaw@sfo.kuramae.ne.jp',
      license='GPL v3',
      packages=['SkypeLogClassic', 'SkypeLogClassic/locales'],
      scripts=['skypelogconvclassic'],
      zip_safe=False)
