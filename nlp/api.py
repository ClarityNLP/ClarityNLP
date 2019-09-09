#!/usr/bin/env python
from flask import Flask
from flask_cors import CORS
import util

def create_app(config_filename=None):

    clarity_app = Flask(__name__)
    clarity_app.debug = True

    if config_filename:
        clarity_app.config.from_pyfile(config_filename)

    from apis import ohdsi_app, phenotype_app, algorithm_app, utility_app
    clarity_app.register_blueprint(ohdsi_app)
    clarity_app.register_blueprint(phenotype_app)
    clarity_app.register_blueprint(algorithm_app)
    clarity_app.register_blueprint(utility_app)

    return clarity_app


# needs to be visible to Flask via import
app = create_app()
CORS(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=util.debug_mode)
