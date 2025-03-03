from setuptools import setup, find_packages

name = 'ABRSQOL'

extra_test = ['pytest>=4', 'pytest-cov>=2',]
extra_dev = [*extra_test,'twine>=4.0.2',]
extra_ci = [*extra_test,'python-coveralls',]

with open('./README.md', 'r') as f:
    long_description = f.read()

setup(
    name=name,
    version="1.0.3",
    description='Numerical solution algorithm to invert a quality of life measure.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Ahlfeldt/ABRSQOL-toolkit-python',
    author='Gabriel M Ahlfeldt',
    author_email='g.ahlfeldt@hu-berlin.de',
    license='MIT',
    install_requires=['numpy','pandas',],
    packages=[name],
    extras_require={
        'test': extra_test,
        'dev': extra_dev,
        'ci': extra_ci,
    },
    entry_points={
        'console_scripts': [
            'ABRSQOL_testdata=ABRSQOL:testdata',
            'ABRSQOL_invert_quality_of_life=ABRSQOL:invert_quality_of_life',
        ],
    },
    classifiers=[

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
