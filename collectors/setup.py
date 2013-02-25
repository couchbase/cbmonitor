from setuptools import setup

version = '0.1.3'

setup(
    name='cbagent',
    version=version,
    url="https://github.com/couchbase/cbmonitor",
    classifiers=[
        "Intended Audience :: Developers",
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        "Operating System :: POSIX",
        "License :: OSI Approved :: Apache Software License",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Terminals'
    ],
    author="Couchbase",
    author_email="admin@couchbase.com",
    license="Apache Software License",
    packages=[
        "cbagent",
        "cbagent.collectors",
        "cbagent.stores",
        "cbagent.collectors.libstats"
    ],
    py_modules=[
        "atop_collector",
        "ns_collector"
    ],
    entry_points={
        'console_scripts': [
            'ns_collector = ns_collector:main',
            'atop_collector = atop_collector:main',
            'at_collector = at_collector:main',
        ]
    },
    include_package_data=True,
    install_requires=[
        'requests==1.0.4',
        'seriesly==0.3.3',
        'fabric==1.5.3',
        'argparse==1.2.1',
        'eventlet==0.12.1',
        'ujson==1.23',
    ],
)
