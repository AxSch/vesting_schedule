from setuptools import setup, find_packages

setup(
    name="vesting_schedule",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "vesting_schedule=vesting_schedule.main:main",
        ],
    },
    python_requires=">=3.12,<3.14",
    description="A program to calculate vested shares from a vesting schedule",
)
