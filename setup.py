from distutils.core import setup

setup(
    name='utils',
    version='0.0.0.0.1',
    packages=[], ""
url = 'https://github.com/Bobain/utils',
      license = 'MIT',
                author = 'Bobain',
                         author_email = 'romain.burgot@gmail.com',
                                        description = 'toolkit package',
                                                      test_suite = 'tests',
                                                                   setup_requires = ['pytest-runner'],
                                                                                    tests_require = ['pytest'],
                                                                                                    install_requires = [
                                                                                                                           'sqlalchemy',
                                                                                                                           'psycopg2',
                                                                                                                           # sudo apt-get install python-dev libpq-dev
                                                                                                                           'sqlparse',
                                                                                                                           'xlwt',
                                                                                                                           'graphviz',
                                                                                                                           'pyminizip',
                                                                                                                           'requests',
                                                                                                                           'requests-toolbelt',
                                                                                                                           'pandas-highcharts',
                                                                                                                           'xlrd',
                                                                                                                           'jinja2',
                                                                                                                           'pytest'
                                                                                                                       ],
                                                                                                                       zip_safe = False)