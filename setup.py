from setuptools import setup, find_packages


setup(
    name='alocarbot',
    packages=find_packages(),
    install_requires=['requests', 'beautifulsoup4', 'robobrowser',
                      'dataset', 'python-telegram-bot'],
    entry_points={
        'console_scripts': [
            'alocarbot = alocarbot.__main__:run',
        ],
    },

)
