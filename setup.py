from setuptools import setup, find_packages

setup(
    name='flatulent',
    version='0.1.0',
    description='Flatulent é uma biblioteca de compressão que combina o algoritmo LZW com a codificação de Huffman '
                'para obter taxas de compressão eficientes. Voltada para ambientes sem threading, como Lambda '
                'Functions.',
    author='Isaias Velasquez',
    author_email='vlaskz@icloud.com',
    url='https://github.com/vlaskz/flatulent',
    packages=find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
