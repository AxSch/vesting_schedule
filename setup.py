from setuptools import setup, find_packages

setup(
    name="vesting_schedule",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "vesting_schedule=vesting_schedule.main:main",
        ],
    },
    python_requires="3.13",
    description="A program to calculate vested shares from a vesting schedule",
)
