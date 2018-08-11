from setuptools import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='dataslots',
    packages=['dataslots'],
    version='1.0.1',
    description='Decorator to add __slots__ in dataclasses',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Adrian Stachlewski',
    author_email='starhel.github@gmail.com',
    url='https://github.com/starhel/dataslots',
    keywords=['dataslots', 'slots', 'dataclasses'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers"
    ],
    install_requires=[
        'dataclasses>=0.6;python_version=="3.6"',
    ],
    python_requires='>=3.6'
)
