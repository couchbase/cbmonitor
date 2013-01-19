from setuptools import setup

version = '1.0.2'

setup(
    name='cbtop',
    version=version,
    description="cbtop wrapper",
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
    keywords=['couchbase', 'terminal', 'top', 'seriesly'],
    author="Couchbase",
    author_email="admin@couchbase.com",
    license="Apache Software License",
    packages=["libcbtop", "metadata"],
    py_modules=["cbtop", "TestInput"],
    entry_points={
        'console_scripts': ['cbtop = cbtop:cbtop_main']
    },
    include_package_data=True,
    install_requires=[
        'seriesly',
        'blessings',
        'tabula',
    ],
)
