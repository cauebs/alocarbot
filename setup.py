from setuptools import setup


setup(
    name='alocarbot',
    py_modules=['alocarbot'],
    install_requires=['requests', 'beautifulsoup4', 'robobrowser',
                      'dataset', 'python-telegram-bot'],
    entry_points={
        'console_scripts': [
            'alocarbot = alocarbot:run',
        ],
    },

)
