from setuptools import setup

version = '0.3'

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
        "ns_collector",
        "at_collector",
        "latency_collector",
        "TestInput"
    ],
    entry_points={
        'console_scripts': [
            'ns_collector = ns_collector:main',
            'atop_collector = atop_collector:main',
            'at_collector = at_collector:main',
            'latency_collector = latency_collector:main',
        ]
    },
    include_package_data=True,
    install_requires=[
        'cbtestlib==1.0.0',
        'requests==1.2.0',
        'seriesly==0.5.2',
        'fabric==1.6.0',
        'argparse==1.2.1',
        'eventlet==0.12.1',
        'ujson==1.23',
    ],
)
