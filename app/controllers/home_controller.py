from flask import Blueprint, render_template
from controllers.compromisso_controller import (
    montar_compromissos_com_pessoas,
    obter_compromisso_repository,
)

home_controller = Blueprint("home", __name__)

@home_controller.route("/", methods=["GET"])
def index():
    compromissos = obter_compromisso_repository().buscar_todos()

    return render_template(
        "index.html",
        compromissos=montar_compromissos_com_pessoas(compromissos),
    )
