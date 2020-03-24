from pathlib import Path

from setuptools import setup


def read_requirements(name: str):
    p = Path(__file__).parent.joinpath(name)
    reqs = [line for line in p.read_text().splitlines() if line]
    return reqs


setup(
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
    },
    package_data={'git_watcher': ['logging.conf']},
)
