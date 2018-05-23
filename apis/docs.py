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
