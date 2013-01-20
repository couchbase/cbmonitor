from setuptools import setup

setup(
    name="priority15",
    entry_points={
        "console_scripts": [
            "plotter = plotter:main",
            "cbstats_json = cbstats_json:main",
            "cbstats_seriesly = cbstats_seriesly:main",
            "ns_to_seriesly = ns_to_seriesly:main",
        ],
    },
)
