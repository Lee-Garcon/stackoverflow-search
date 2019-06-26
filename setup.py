

from setuptools import setup

setup(
    name="stackoverflow-search",
    version="0.1.0",
    packages=["so_search"],
    entry_points={
        "console_scripts": ["so-search=so_search.__main__:main"]
    },
    install_requires=["requests", "bs4"],
)
