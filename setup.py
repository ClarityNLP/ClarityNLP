from setuptools import setup

setup(
    name='ClarityNLP',
    version='0.1.13',
    packages=[''],
    url='https://github.com/ClarityNLP/ClarityNLP',
    license='MPL',
    author='GTRI Health Team',
    author_email='charity.hilton@gtri.gatech.edu',
    description='An NLP framework for clinical phenotyping.',
    install_requires=['flask', 'yos_social_sdk', 'requests', 'pymongo', 'recommonmark', 'nltk', 'luigi',
                      'spacy', 'textacy', 'simplejson', 'pandas', 'inflect', 'bson', 'beautifulsoup4', 'ordereddict',
                      'pymysql', 'vocabulary']
)
