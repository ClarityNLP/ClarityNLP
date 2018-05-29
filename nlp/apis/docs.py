from flask import Blueprint
from flask_autodoc import Autodoc


doc = Blueprint('doc', __name__, url_prefix='/documentation')
auto = Autodoc()


@doc.route('/')
@doc.route('/public')
def public_doc():
    return auto.html(groups=['public'], title='ClarityNLP Documentation')


@doc.route('/private')
def private_doc():
    return auto.html(groups=['private'], title='Private Documentation')


@doc.route('/algorithms')
def algorithms_doc():
    return auto.html(groups=['algorithms'], title='Algorithms Documentation')


@doc.route('/omop_ohdsi')
def omop_doc():
    return auto.html(groups=['omop', 'ohdsi'], title='OMOP/OHDSI Documentation')


@doc.route('/phenotype')
def phenotype_doc():
    return auto.html(groups=['phenotypes'], title='Phenotype Documentation')


@doc.route('/utility')
def utility_doc():
    return auto.html(groups=['utilities'], title='Utility Documentation')
