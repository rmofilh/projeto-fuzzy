"""Composition root do projeto.

Responsabilidade única: construir e expor a aplicação Flask (registro do
blueprint). Não há lógica fuzzy, de negócio ou de apresentação aqui.
"""

from flask import Flask

from src.presentation.routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(api)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)