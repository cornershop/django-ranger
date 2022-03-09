import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__),
                           'README.md')).read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-ranger',
    version='0.4.2',
    packages=['django_ranger', 'django_ranger.migrations'],
    include_package_data=True,
    license='BSD License',
    description='Parametrized Role Based Access Control (PRBAC) system',
    long_description=README,
    url='https://github.com/cornershop/django-ranger',
    author='Richard Barrios',
    author_email='richard@cornershoapp.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ]
)