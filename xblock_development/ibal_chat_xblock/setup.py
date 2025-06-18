"""Setup for ibal_chat_xblock XBlock."""

import os
from setuptools import setup

def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.
    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}

setup(
    name='ibal_chat_xblock',
    version='0.1',
    description='IBAL Chat XBlock - An interactive chat interface for OpenEdX',
    license='AGPL v3',
    packages=[
        'ibal_chat_xblock',
    ],
    install_requires=[
        'XBlock',
        'xblock-utils',
    ],
    entry_points={
        'xblock.v1': [
            'ibal_chat = ibal_chat_xblock:IBALChatXBlock',
        ]
    },
    package_data=package_data("ibal_chat_xblock", ["static", "public", "translations"]),
) 