from datetime import date, datetime, timedelta

from flask import Blueprint, render_template

from helpers.compromissos import montar_compromissos_com_pessoas
from helpers.periodo import (
    PERIODOS,
    filtrar_compromissos_por_periodo,
    obter_periodo,
)
from helpers.repositorios import obter_compromisso_repository

home_controller = Blueprint("home", __name__)


@home_controller.route("/", methods=["GET"])
def index():
    periodo = obter_periodo()
    compromissos = obter_compromisso_repository().buscar_todos()

    agora = datetime.now()
    limite = agora + timedelta(days=7)

    resumo = {
        "proximos_7": sum(
            1 for c in compromissos if agora <= c.data_horario <= limite
        ),
        "total": len(compromissos),
        "sem_pessoas": sum(1 for c in compromissos if not c.pessoas),
    }

    return render_template(
        "index.html",
        compromissos=montar_compromissos_com_pessoas(
            filtrar_compromissos_por_periodo(compromissos, periodo)
        ),
        periodo=periodo,
        titulo_lista=PERIODOS[periodo],
        resumo=resumo,
        hoje=date.today().isoformat(),
    )
