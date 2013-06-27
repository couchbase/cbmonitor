from setuptools import setup

version = '0.5.2'

setup(
    name='cbagent',
    version=version,
    author='Couchbase',
    license='Apache Software License',
    packages=[
        'cbagent',
        'cbagent.cli',
        'cbagent.collectors',
        'cbagent.collectors.libstats'
    ],
    entry_points={
        'console_scripts': [
            'ns_collector = cbagent.cli.ns_collector:main',
            'atop_collector = cbagent.cli.atop_collector:main',
            'at_collector = cbagent.cli.at_collector:main',
        ]
    },
    include_package_data=True,
    install_requires=[
        'argparse==1.2.1',
        'eventlet==0.12.1',
        'fabric==1.6.0',
        'logger',
        'requests==1.2.0',
        'seriesly',
        'ujson==1.23',
    ],
)
