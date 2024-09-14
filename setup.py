# -*- coding: utf-8 -*-

from setuptools import setup

requirements = [
    'people_recognition_models>=0.3.0',
    'Click>=6.0',
    'dlib>=19.7',
    'numpy',
    'Pillow'
]

test_requirements = [
    'tox',
    'flake8'
]

setup(
    name='people_recognition',
    version='1.4.0',
    description="Recognize peoples from Python or from the command line",
    long_description=readme + '\n\n' + history,
    author="Adam Geitgey",
    author_email='ageitgey@gmail.com',
    packages=[
        'people_recognition',
    ],
    package_dir={'people_recognition': 'people_recognition'},
    package_data={
        'people_recognition': ['models/*.dat']
    },
    entry_points={
        'console_scripts': [
            'people_recognition=people_recognition.people_recognition_cli:main',
            'people_detection=people_recognition.people_detection_cli:main'
        ]
    },
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='people_recognition',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
