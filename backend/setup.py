import setuptools

description = """\
A mobile app that lets you plan group meetings and find optimal connections
using means of public transport based on GTFS Static data feed published by Kraków Public Transport Authority."""

setuptools.setup(
    name='krk_meetings',
    version='0.1.0',
    description=description,
    url='https://github.com/wietlabs/krk_meetings',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.8',
)
