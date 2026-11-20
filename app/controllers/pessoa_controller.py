from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
)
from pymongo.errors import DuplicateKeyError

from helpers.repositorios import obter_pessoa_repository
from models.pessoa import Pessoa
from validators.pessoa_validator import PessoaValidador

pessoa_controller = Blueprint("pessoas", __name__)

@pessoa_controller.route("/pessoas", methods=["GET"])
def index():
    repository = obter_pessoa_repository()
    return render_template(
        "pessoas/index.html",
        pessoas=repository.buscar_todos(),
        erros={},
        formulario={}
    )

@pessoa_controller.route("/pessoas/criar", methods=["POST"])
def criar():
    repository = obter_pessoa_repository()
    validator = PessoaValidador(request.form, repository)

    if not validator.eh_valido():
        return render_template(
            "pessoas/index.html",
            erros=validator.erros,
            formulario=request.form,
            pessoas=repository.buscar_todos()
        ), 400

    try: 
        nova_pessoa = Pessoa(**validator.dados_limpos)
        repository.criar(nova_pessoa)
    except DuplicateKeyError:
        return render_template(
            "pessoas/index.html",
            erros={"email" : "Este e-mail já está cadastrado."},
            formulario=request.form,
            pessoas=repository.buscar_todos(),
        ),400

    return redirect(url_for("pessoas.index"))