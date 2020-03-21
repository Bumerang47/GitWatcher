from setuptools import setup
from pathlib import Path


def read_requirements(name: str):
    p = Path(__file__).parent.joinpath(name)
    reqs = [line for line in p.read_text().splitlines() if line]
    return reqs


setup(
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
    },
)
