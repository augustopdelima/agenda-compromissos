from flask import Blueprint, g, current_app, request, render_template, redirect, url_for
from models.compromisso import Compromisso
from repositories.compromisso_repository import CompromissoRepository
from repositories.pessoa_repository import PessoaRepository
from validators.compromisso_validator import CompromissoValidador

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

def obter_dados_formulario() -> dict:
    return {
        "data_horario": request.form.get("data_horario", ""),
        "titulo": request.form.get("titulo", ""),
        "descricao": request.form.get("descricao", ""),
        "pessoas": request.form.getlist("pessoas"),
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

@compromisso_controller.route("/", methods=["GET"])
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
