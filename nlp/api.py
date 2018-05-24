from flask import Flask


def create_app(config_filename=None):
    clarity_app = Flask(__name__)
    clarity_app.debug = True

    from apis import auto
    auto.init_app(clarity_app)

    if config_filename:
        clarity_app.config.from_pyfile(config_filename)

    from apis import ohdsi_app, phenotype_app, algorithm_app, utility_app, doc
    clarity_app.register_blueprint(ohdsi_app)
    clarity_app.register_blueprint(phenotype_app)
    clarity_app.register_blueprint(algorithm_app)
    clarity_app.register_blueprint(utility_app)
    clarity_app.register_blueprint(doc)

    return clarity_app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, threaded=True)
