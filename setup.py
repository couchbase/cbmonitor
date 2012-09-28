from setuptools import setup, find_packages

version = '1.0.1'

setup(
    name = 'cbtop',
    version = version,
    description = "cbtop wrapper",
    url = "https://github.com/couchbaselabs/priority15",
    long_description = open("README.md").read(),
    classifiers = [
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
    keywords = ['couchbase', 'terminal', 'top', 'seriesly'],
    author = "couchbase",
    author_email = "admin@couchbase.com",
    license="Apache Software License",
    packages = find_packages(exclude=['ez_setup']),
    include_package_data = True,
    install_requires = [
        'seriesly',
        'blessings',
        'tabula',
        ],
)
