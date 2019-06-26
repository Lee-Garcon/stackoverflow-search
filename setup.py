from setuptools import setup

setup(
    name="stackoverflow-search",
    version="0.1.0",
    packages=["requests", "bs4"],
    entry_points={
        "console_scripts": ["so-search = stackoverflow_search.__main__:main"]
    },
)
