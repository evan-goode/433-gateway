#!/usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name="433-gateway",
    version="1.0.0",
    description="",
    url="https://github.com/evan-goode/433-gateway",
    author="Evan Goode",
    author_email="mail@evangoo.de",
    license="AGPLv3",
    install_requires=["rpi-rf", "paho-mqtt", "toml"],
    packages=find_packages(),
    entry_points={"console_scripts": ["433-gateway=433.433:main"]},
)
