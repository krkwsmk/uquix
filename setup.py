from setuptools import setup, find_packages
from pathlib import Path

README = (Path(__file__).parent / "README.md").read_text()

setup(
    name="uquix",
    version="1.0.0",
    description="Ultimate HTTPs request manipulation toolkit for security testing",
    long_description=README,
    long_description_content_type="text/markdown",
    author="0.1Arafa",
    url="https://github.com/0Arafa/uquix",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=False,
    install_requires=[
        "uvloop>=0.19.0",
        "aiodns>=3.2.0",
        "aiohttp>=3.10.10",
        "aiohttp_socks>=0.10.1",
        "aiofiles>=24.1.0",
        "ujson>=5.10.0",
        "fake_useragent>=2.0.3",
    ],
    entry_points={
        "console_scripts": [
            "uquix=uquix.uquix:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
    ],
    python_requires=">=3.9",
)
