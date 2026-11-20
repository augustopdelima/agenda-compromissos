from datetime import datetime

from flask import request

PERIODOS = {
    "proximos": "Futuros compromissos",
    "passados": "Compromissos antigos",
    "todos": "Todos os compromissos",
}


def obter_periodo() -> str:
    periodo = request.args.get("periodo", "todos")
    return periodo if periodo in PERIODOS else "todos"


def filtrar_compromissos_por_periodo(compromissos: list, periodo: str) -> list:
    agora = datetime.now()
    if periodo == "proximos":
        return [c for c in compromissos if c.data_horario >= agora]
    if periodo == "passados":
        return [c for c in compromissos if c.data_horario < agora]
    return compromissos
