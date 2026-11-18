import os
from flask import Flask
from pymongo import MongoClient
from repositories.pessoa_repository import PessoaRepository
from repositories.compromisso_repository import CompromissoRepository
from controllers.pessoa_controller import pessoa_controller
from controllers.compromisso_controller import compromisso_controller
from controllers.home_controller import home_controller

def iniciar_app():
    app = Flask(__name__)

    client = MongoClient(os.environ["MONGO_URI"])
    app.db = client[os.environ["MONGO_DATABASE"]]

    PessoaRepository(app.db).garantir_indices()
    CompromissoRepository(app.db).garantir_indices()

    app.register_blueprint(home_controller)
    app.register_blueprint(pessoa_controller)
    app.register_blueprint(compromisso_controller, url_prefix="/compromissos")

    return app

if __name__ == "__main__":
    app = iniciar_app()
    app.run(debug=True)
