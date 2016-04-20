from distutils.core import setup

setup(
    name='utils',
    version='0.0.0.0.1',
    packages=[],
    url = 'https://github.com/Bobain/utils',
    license = 'MIT',
    author = 'Bobain',
    author_email = 'romain.burgot@gmail.com',
    description = 'toolkit package',
    test_suite = 'tests',
    setup_requires = ['pytest-runner'],
    tests_require = ['pytest'],
    install_requires = [
        'pytest',
        'pyminizip',
        'requests',
        'requests-toolbelt',
        'pandas',
        'jinja2',
        'xlwt',
        'xlrd',
        'xlutils'
        ],
    zip_safe = False)