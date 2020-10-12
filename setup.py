# -*- coding: utf-8 -*-
"""Setup for the `aiida-3dd` CLI."""
import fastentrypoints  # pylint: disable=unused-import,import-error


def setup_package():
    """Set up the package."""
    import json
    from setuptools import setup, find_packages

    with open('setup.json', 'r') as handle:
        setup_json = json.load(handle)

    setup(include_package_data=True, packages=find_packages(include=['aiida_3dd', 'aiida_3dd.*']), **setup_json)


if __name__ == '__main__':
    setup_package()
