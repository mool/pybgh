import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

print(setuptools.find_packages())

setuptools.setup(
    name='pybgh',
    version='0.1.1',
    author='Pablo Gutierrez del Castillo',
    author_email='pablogutierrezdelc@gmail.com',
    description='A BGH Smart devices API client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mool/pybgh',
    keywords='BGH',
    install_requires=['requests'],
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
