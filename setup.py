import os

from setuptools import setup


readme_path = os.path.join(os.path.dirname(__file__), "README.rst")
with open(readme_path) as fp:
    long_description = fp.read()

setup(
    name='imdbparser',
    version='1.0.22',
    url='https://github.com/JohnDoee/imdbparser',
    author='John Doee',
    author_email='johndoee@tidalstream.org',
    description='IMDB Parser',
    long_description=long_description,
    license='MIT',
    packages=['imdbparser'],
    install_requires=['lxml', 'requests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries :: Python Modules',
   ]
)
