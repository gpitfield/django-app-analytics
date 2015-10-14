import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-app-analytics',
    version='0.1',
    packages=[
        'analytics', 'analytics.migrations',
        'analytics.management', 'analytics.management.commands',
        'analytics.templates', 'analytics.views',
    ],
    install_requires=[
        'Django>=1.7',
    ],
    include_package_data=True,
    license='BSD License',
    description='A Django app for registering (and eventually analyzing) analytics.',
    long_description=README,
    url='http://www.example.com/',
    author='Geoff Pitfield',
    author_email='geoff@pitfield.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)