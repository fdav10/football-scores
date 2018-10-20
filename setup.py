from setuptools import setup, find_packages

setup(
    name="FootieScores",
    packages=find_packages(),
    scripts=['bin/fs_start_updater.sh']
)
