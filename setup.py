# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = __import__('ndator').__version__

setup(
    name='django-ndator',
    version=version,
    author='Nikita Zubkov',
    author_email='zubchick@gmail.com',
    url='http://github.com/zubchick/django-ndator',
    description='Django models obfuscator',
    long_description=open('README.rst').read(),
    license='New BSD License',
    install_requires=['setuptools'],
    packages=find_packages(),
    zip_safe=False,

    classifiers=[
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        ],
)
