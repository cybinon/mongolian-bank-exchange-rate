"""
Монгол банкны валютын ханш цуглуулагч - Package тохиргоо.
"""
from setuptools import setup, find_packages
import os

# README файлыг уншиж long_description болгох
def read_file(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read()

# Хувилбарыг VERSION файлаас эсвэл git tag-аас авах
def get_version():
    if os.path.exists('VERSION'):
        with open('VERSION', 'r') as f:
            return f.read().strip()
    return '1.0.0'

setup(
    name='mongolian-bank-exchange-rate',
    version=get_version(),
    author='btseee',
    author_email='your.email@example.com',
    description='Mongolian Bank Exchange Rate Crawler - 13 банкны валютын ханш цуглуулагч',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/btseee/mongolian-bank-exchange-rate',
    project_urls={
        'Bug Reports': 'https://github.com/btseee/mongolian-bank-exchange-rate/issues',
        'Source': 'https://github.com/btseee/mongolian-bank-exchange-rate',
        'Documentation': 'https://github.com/btseee/mongolian-bank-exchange-rate#readme',
    },
    packages=find_packages(exclude=['tests', 'docs']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Framework :: FastAPI',
    ],
    python_requires='>=3.8',
    install_requires=[
        'fastapi>=0.104.0',
        'uvicorn[standard]>=0.24.0',
        'sqlalchemy>=2.0.0',
        'python-dotenv>=1.0.0',
        'schedule>=1.2.0',
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.0',
        'playwright>=1.40.0',
        'lxml>=4.9.0',
    ],
    extras_require={
        'dev': [
            'black>=23.0.0',
            'flake8>=6.0.0',
            'isort>=5.12.0',
            'pylint>=3.0.0',
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ],
        'postgres': ['psycopg2-binary>=2.9.0'],
        'mysql': ['pymysql>=1.0.0'],
    },
    entry_points={
        'console_scripts': [
            'mongolian-bank-api=app.api.main:main',
            'mongolian-bank-cron=cron:main',
        ],
    },
    include_package_data=True,
    keywords='mongolia bank exchange rate currency api fastapi crawler scraper финанс валют ханш монгол банк',
    zip_safe=False,
)
