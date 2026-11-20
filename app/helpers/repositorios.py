from flask import abort, current_app, g

from models.compromisso import Compromisso
from repositories.compromisso_repository import CompromissoRepository
from repositories.pessoa_repository import PessoaRepository


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
