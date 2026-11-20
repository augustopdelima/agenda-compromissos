from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
)
from pymongo.errors import DuplicateKeyError

from helpers.formulario import obter_dados_edicao, obter_url_retorno
from helpers.renderizacao import renderizar_edicao_pessoa
from helpers.repositorios import obter_pessoa_ou_404, obter_pessoa_repository
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

    flash("Pessoa cadastrada com sucesso.", "success")
    return redirect(url_for("pessoas.index"))


@pessoa_controller.route("/pessoas/<id>/editar", methods=["GET"])
def editar(id):
    pessoa = obter_pessoa_ou_404(id)
    return renderizar_edicao_pessoa(pessoa, {})


@pessoa_controller.route("/pessoas/<id>/editar", methods=["POST"])
def atualizar(id):
    pessoa = obter_pessoa_ou_404(id)
    repository = obter_pessoa_repository()
    formulario = obter_dados_edicao(PessoaValidador.CAMPOS_EDICAO)
    validator = PessoaValidador(
        formulario,
        repository,
        modo="edicao",
        id_pessoa=id,
    )

    if not validator.eh_valido():
        return renderizar_edicao_pessoa(pessoa, formulario, validator.erros, 400)

    try:
        repository.atualizar(id, validator.dados_limpos)
    except DuplicateKeyError:
        return renderizar_edicao_pessoa(
            pessoa,
            formulario,
            {"email": "Este e-mail já está cadastrado."},
            400,
        )

    flash("Pessoa atualizada com sucesso.", "success")
    return redirect(obter_url_retorno(url_for("pessoas.index")))
