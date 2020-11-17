from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='wallabag-client',
    use_scm_version=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/artur-shaik/wallabag-client',
    author='Artur Shaik',
    author_email='artur@shaik.link',
    description=('A command-line client for the self-hosted '
                 '`read-it-later` app Wallabag'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',

    setup_requires=[
        'pytest-runner==5.1',
        'setuptools_scm==3.3.3',
    ],
    install_requires=[
        'beautifulsoup4>=4.9.1',
        'pycryptodome>=3.9.8',
        'requests>=2.11.1',
        'click>=7.0',
        'click_spinner',
        'pyxdg',
        'colorama>=0.4.3',
        'delorean',
        'humanize',
        'lxml',
        'tzlocal<3',
        'tabulate'
    ],
    tests_require=[
        'pytest==4.6.3',
    ],

    entry_points='''
        [console_scripts]
        wallabag=wallabag.wallabag:cli
    '''
)
