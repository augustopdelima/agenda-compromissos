import os
from flask import Flask
from pymongo import MongoClient
from repositories.pessoa_repository import PessoaRepository
from controllers.pessoa_controller import pessoa_controller

def iniciar_app():
    app = Flask(__name__)

    client = MongoClient(os.environ["MONGO_URI"])
    app.db = client[os.environ["MONGO_DATABASE"]]

    PessoaRepository(app.db).garantir_indices()

    app.register_blueprint(pessoa_controller)

    return app

if __name__ == "__main__":
    app = iniciar_app()
    app.run(debug=True)
