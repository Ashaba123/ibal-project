from setuptools import setup

setup(
    name='ibalxbloc',
    version='0.1',
    description='A simple XBlock that displays a welcome message and a Start Chat button.',
    packages=['ibalxbloc'],
    install_requires=[
        'XBlock',
        'python-dotenv', 
    ],
    entry_points={
        'xblock.v1': [
            'ibalxbloc = ibalxbloc.ibalxbloc:IbalXBlock',
        ]
    },
    package_data={
        'ibalxbloc': [
            'static/css/*.css',
            'static/html/*.html',
            'static/js/src/*.js',
            'static/README.txt',
            'translations/README.txt',
        ]
    },
) 