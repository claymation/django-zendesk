import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-zendesk",
    version = "0.0.1",
    author = "Clay McClure",
    author_email = "clay@daemons.net",
    url = 'https://github.com/claymation/django-zendesk',
    description = "Django application for handling HTTP target callbacks from Zendesk.",
    keywords = "zendesk",
    packages = ['djzendesk'],
    long_description = read('README'),
    classifiers = [
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: BSD License",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
    ],
)
