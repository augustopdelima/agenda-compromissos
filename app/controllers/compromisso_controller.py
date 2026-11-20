from flask import Blueprint, g, current_app, request, render_template, redirect, url_for, abort
from models.compromisso import Compromisso
from repositories.compromisso_repository import CompromissoRepository
from repositories.pessoa_repository import PessoaRepository
from validators.compromisso_validator import CompromissoValidador

compromisso_controller = Blueprint("compromisso", __name__)


def obter_compromisso_repository() -> CompromissoRepository:
    if "compromisso_repository" not in g:
        g.compromisso_repository = CompromissoRepository(current_app.db)
    return g.compromisso_repository


def obter_pessoa_repository() -> PessoaRepository:
    if "pessoa_repository" not in g:
        g.pessoa_repository = PessoaRepository(current_app.db)
    return g.pessoa_repository


def obter_compromisso_ou_404(id: str) -> Compromisso:
    compromisso = obter_compromisso_repository().buscar_por_id(id)
    if compromisso is None:
        abort(404)
    return compromisso


def montar_compromissos_com_pessoas(compromissos: list) -> list[dict]:
    ids_pessoas = [
        id_pessoa
        for compromisso in compromissos
        for id_pessoa in compromisso.pessoas
    ]

    pessoas = obter_pessoa_repository().buscar_por_ids(ids_pessoas)
    pessoas_por_id = {pessoa.id: pessoa for pessoa in pessoas}

    return [
        {
            "compromisso": compromisso,
            "pessoas": [
                pessoas_por_id[id_pessoa]
                for id_pessoa in compromisso.pessoas
                if id_pessoa in pessoas_por_id
            ]
        }
        for compromisso in compromissos
    ]


def obter_dados_formulario() -> dict:
    return {
        "data_horario": request.form.get("data_horario", ""),
        "titulo": request.form.get("titulo", ""),
        "descricao": request.form.get("descricao", ""),
        "pessoas": request.form.getlist("pessoas"),
    }


def obter_dados_edicao() -> dict:
    return {
        campo: request.form[campo]
        for campo in CompromissoValidador.CAMPOS_EDICAO
        if campo in request.form
    }


def renderizar_index(erros: dict | None = None, formulario: dict | None = None, codigo_status: int = 200):
    compromissos = obter_compromisso_repository().buscar_todos()
    pessoas = obter_pessoa_repository().buscar_todos()

    return render_template(
        "compromissos/index.html",
        compromissos=montar_compromissos_com_pessoas(compromissos),
        pessoas=pessoas,
        erros=erros or {},
        formulario=formulario or {},
    ), codigo_status


def renderizar_edicao(
    compromisso: Compromisso,
    formulario: dict,
    erros: dict | None = None,
    codigo_status: int = 200,
):
    pessoas = montar_compromissos_com_pessoas([compromisso])[0]["pessoas"]

    return render_template(
        "compromissos/editar.html",
        compromisso=compromisso,
        pessoas=pessoas,
        erros=erros or {},
        formulario=formulario,
    ), codigo_status


@compromisso_controller.route("/", methods=["GET"], strict_slashes=False)
def index():
    return renderizar_index()


@compromisso_controller.route("/criar", methods=["POST"])
def criar():
    formulario = obter_dados_formulario()
    validator = CompromissoValidador(formulario, obter_pessoa_repository())

    if not validator.eh_valido():
        return renderizar_index(validator.erros, formulario, 400)

    obter_compromisso_repository().criar(Compromisso(**validator.dados_limpos))
    return redirect(url_for("compromisso.index"))


@compromisso_controller.route("/<id>/editar", methods=["GET"])
def editar(id):
    compromisso = obter_compromisso_ou_404(id)
    return renderizar_edicao(compromisso, {})


@compromisso_controller.route("/<id>/editar", methods=["POST"])
def atualizar(id):
    compromisso = obter_compromisso_ou_404(id)
    formulario = obter_dados_edicao()
    validator = CompromissoValidador(formulario, modo="edicao")

    if not validator.eh_valido():
        return renderizar_edicao(compromisso, formulario, validator.erros, 400)

    obter_compromisso_repository().atualizar_titulo_descricao(
        id, validator.dados_limpos
    )
    return redirect(url_for("compromisso.index"))


@compromisso_controller.route("/<id>/excluir", methods=["POST"])
def excluir(id):
    obter_compromisso_ou_404(id)
    obter_compromisso_repository().excluir(id)
    return redirect(url_for("compromisso.index"))
