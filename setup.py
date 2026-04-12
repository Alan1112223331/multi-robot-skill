"""
Setup script for multi_robot_skill package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="multi_robot_skill",
    version="2.2.0",
    author="Claude Code",
    description="Multi-Robot Coordination Skill for AI Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Alan1112223331/multi-robot-skill",
    packages=find_packages() + ['multi_robot_skill'],
    package_dir={'multi_robot_skill': '.'},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "multi-robot-skill=multi_robot_skill.cli:main",
        ],
    },
)
