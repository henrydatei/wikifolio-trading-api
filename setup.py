from setuptools import setup

setup(
    name='wikifolioTradingAPI',
    version='1.0.0',
    description='Wikifolio Trading API Wrapper',
    author='henrydatei',
    author_email='henrydatei@web.de',
    url='https://github.com/henrydatei/wikifolio-trading-api',
    packages=['wikifolioTradingAPI'],
    install_requires=[
        "requests",
        "dacite"
    ],
)