from setuptools import setup, find_packages

setup(
    name='pegscanner_backend',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # Dependencies listed in requirements.txt will be handled by pip install -r
        # 'yfinance', 
    ],
    entry_points={
        'console_scripts': [
            'pegscanner-backend = backend.src.main:main',
        ],
    },
)
