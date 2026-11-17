from flask import Blueprint, g, current_app, request, render_template, redirect, url_for
from repositories.compromisso_repository import CompromissoRepository
from repositories.pessoa_repository import PessoaRepository

compromisso_controller = Blueprint("compromisso",__name__)

def obter_compromisso_repository() -> CompromissoRepository:
    if "compromisso_repository" not in g:
        g.compromisso_repository = CompromissoRepository(current_app.db)
    return g.compromisso_repository

def obter_pessoa_repository() -> PessoaRepository:
    if "pessoa_repository" not in g:
        g.pessoa_repository = PessoaRepository(current_app.db)
    return g.pessoa_repository

def montar_compromissos_com_pessoas(compromissos: list) -> list[dict]:
    pessoa_repository = obter_pessoa_repository()

    return [
        {
            "compromisso": compromisso,
            "pessoas": pessoa_repository.buscar_por_ids(compromisso.pessoas)
        }
        for compromisso in compromissos
    ]

@compromisso_controller.route("/", methods=["GET"])
def index():
    repository = obter_compromisso_repository()
    compromissos = repository.buscar_todos()
    return render_template(
        "compromisso/index.html",
        compromissos=montar_compromissos_com_pessoas(compromissos),
        erros={},
    )