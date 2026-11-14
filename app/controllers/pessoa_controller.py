from flask import Blueprint, g, current_app, request, render_template, redirect, url_for
from pymongo.errors import DuplicateKeyError
from models.pessoa import Pessoa
from repositories.pessoa_repository import PessoaRepository
from validators.pessoa_validator import PessoaValidador

pessoa_controller = Blueprint("pessoas",__name__)

def obter_pessoa_repository() -> PessoaRepository:
    if "pessoa_repository" not in g:
        g.pessoa_repository = PessoaRepository(current_app.db)
    return g.pessoa_repository

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