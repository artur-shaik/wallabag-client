from setuptools import find_packages, setup

setup(
    name='wallabag-client',
    use_scm_version=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/artur-shaik/wallabag-client',
    author='Artur Shaik',
    description='A command-line client for the self-hosted \
            read-it-later app Wallabag',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

    setup_requires=[
        'pytest-runner==5.1',
        'setuptools_scm==3.3.3',
        'wheel',
    ],
    install_requires=[
        'beautifulsoup4>=4.5.1',
        'pycryptodome>=3.9.8',
        'requests>=2.11.1',
    ],
    tests_require=[
        'pytest==4.6.3',
    ],

    entry_points='''
        [console_scripts]
        wallabag=wallabag.wallabag:cli
    '''
)
