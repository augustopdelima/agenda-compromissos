from datetime import date

from flask import render_template, url_for

from helpers.compromissos import montar_compromissos_com_pessoas
from helpers.formulario import obter_url_cancelar, obter_url_retorno
from helpers.periodo import (
    PERIODOS,
    filtrar_compromissos_por_periodo,
    obter_periodo,
)
from helpers.repositorios import (
    obter_compromisso_repository,
    obter_pessoa_repository,
)
from models.compromisso import Compromisso


def renderizar_index(
    erros: dict | None = None,
    formulario: dict | None = None,
    codigo_status: int = 200,
):
    periodo = obter_periodo()
    compromissos = obter_compromisso_repository().buscar_todos()
    pessoas = obter_pessoa_repository().buscar_todos()

    return render_template(
        "compromissos/index.html",
        compromissos=montar_compromissos_com_pessoas(
            filtrar_compromissos_por_periodo(compromissos, periodo)
        ),
        pessoas=pessoas,
        erros=erros or {},
        formulario=formulario or {},
        periodo=periodo,
        titulo_lista=PERIODOS[periodo],
        hoje=date.today().isoformat(),
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
        url_cancelar=obter_url_retorno(
            obter_url_cancelar(
                url_for("compromisso.detalhes", id=compromisso.id)
            )
        ),
        hoje=date.today().isoformat(),
    ), codigo_status


def renderizar_detalhes(compromisso: Compromisso):
    pessoas = montar_compromissos_com_pessoas([compromisso])[0]["pessoas"]

    return render_template(
        "compromissos/detalhes.html",
        compromisso=compromisso,
        pessoas=pessoas,
    )


def renderizar_pessoas(
    compromisso: Compromisso,
    formulario: dict,
    erros: dict | None = None,
    codigo_status: int = 200,
):
    pessoas = obter_pessoa_repository().buscar_todos()

    return render_template(
        "compromissos/pessoas.html",
        compromisso=compromisso,
        pessoas=pessoas,
        formulario=formulario,
        erros=erros or {},
        url_cancelar=obter_url_retorno(
            obter_url_cancelar(
                url_for("compromisso.detalhes", id=compromisso.id)
            )
        ),
        hoje=date.today().isoformat(),
    ), codigo_status
