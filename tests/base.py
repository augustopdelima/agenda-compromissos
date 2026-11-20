"""Infraestrutura compartilhada pelos testes.

Não usa MongoDB nem dependências além das já exigidas pelo projeto. As classes
"Fake" abaixo implementam apenas o pedaço da API do PyMongo que a aplicação
realmente usa, o que permite testar repositórios e rotas com um banco em memória.
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from bson import ObjectId
from flask import Flask, render_template

RAIZ = Path(__file__).resolve().parents[1]
DIRETORIO_APP = RAIZ / "app"
DIRETORIO_TESTES = Path(__file__).resolve().parent

for diretorio in (str(DIRETORIO_TESTES), str(DIRETORIO_APP)):
    if diretorio not in sys.path:
        sys.path.insert(0, diretorio)

from controllers.compromisso_controller import (  # noqa: E402
    compromisso_controller,
)
from controllers.home_controller import home_controller  # noqa: E402
from controllers.pessoa_controller import pessoa_controller  # noqa: E402


class ResultadoFake:
    def __init__(
        self,
        inserted_id=None,
        matched_count=0,
        deleted_count=0,
        modified_count=0,
    ):
        self.inserted_id = inserted_id
        self.matched_count = matched_count
        self.deleted_count = deleted_count
        self.modified_count = modified_count


class CursorFake:
    def __init__(self, documentos):
        self._documentos = list(documentos)

    def sort(self, campo, ordem=1):
        self._documentos.sort(
            key=lambda documento: (
                documento.get(campo) is None,
                documento.get(campo),
            ),
            reverse=ordem < 0,
        )
        return self

    def __iter__(self):
        return iter(self._documentos)


class ColecaoFake:
    """Coleção em memória com suporte às operações usadas pelos repositórios."""

    def __init__(self):
        self.documentos = []

    def create_index(self, *args, **kwargs):
        return "indice_fake"

    def insert_one(self, dados):
        documento = dict(dados)
        documento.setdefault("_id", ObjectId())
        self.documentos.append(documento)
        return ResultadoFake(inserted_id=documento["_id"])

    def find(self, filtro=None):
        return CursorFake(
            documento
            for documento in self.documentos
            if self._combina(documento, filtro or {})
        )

    def find_one(self, filtro=None):
        for documento in self.documentos:
            if self._combina(documento, filtro or {}):
                return documento
        return None

    def update_one(self, filtro, atualizacao):
        for documento in self.documentos:
            if self._combina(documento, filtro or {}):
                documento.update(atualizacao.get("$set", {}))
                return ResultadoFake(matched_count=1)
        return ResultadoFake(matched_count=0)

    def update_many(self, filtro, atualizacao):
        modificados = 0
        for documento in self.documentos:
            if not self._combina(documento, filtro or {}):
                continue

            documento.update(atualizacao.get("$set", {}))
            for campo, valor in atualizacao.get("$pull", {}).items():
                documento[campo] = [
                    item for item in documento.get(campo, []) if item != valor
                ]
            modificados += 1

        return ResultadoFake(matched_count=modificados, modified_count=modificados)

    def delete_one(self, filtro):
        for indice, documento in enumerate(self.documentos):
            if self._combina(documento, filtro or {}):
                del self.documentos[indice]
                return ResultadoFake(deleted_count=1)
        return ResultadoFake(deleted_count=0)

    @staticmethod
    def _combina(documento, filtro):
        for campo, esperado in filtro.items():
            valor = documento.get(campo)
            if isinstance(esperado, dict) and "$in" in esperado:
                if valor not in esperado["$in"]:
                    return False
            elif isinstance(valor, (list, tuple)):
                if esperado not in valor:
                    return False
            elif valor != esperado:
                return False
        return True


class BancoFake:
    def __init__(self):
        self.colecoes = {}

    def __getitem__(self, nome):
        return self.colecoes.setdefault(nome, ColecaoFake())


def criar_app(db):
    """Monta a aplicação com os mesmos blueprints de app.py, mas sem Mongo."""
    aplicacao = Flask(
        "app_teste",
        template_folder=str(DIRETORIO_APP / "templates"),
        static_folder=str(DIRETORIO_APP / "static"),
    )
    aplicacao.config.update(TESTING=True, SECRET_KEY="chave-de-teste")
    aplicacao.db = db
    aplicacao.register_blueprint(home_controller)
    aplicacao.register_blueprint(pessoa_controller)
    aplicacao.register_blueprint(compromisso_controller, url_prefix="/compromissos")

    @aplicacao.errorhandler(404)
    def pagina_nao_encontrada(erro):
        return render_template("404.html"), 404

    return aplicacao


class BaseTeste(unittest.TestCase):
    def setUp(self):
        self.db = BancoFake()
        self.app = criar_app(self.db)
        self.cliente = self.app.test_client()

    @staticmethod
    def html(resposta):
        return resposta.get_data(as_text=True)

    def criar_pessoa(self, nome="Ana", email="ana@exemplo.com"):
        from models.pessoa import Pessoa
        from repositories.pessoa_repository import PessoaRepository

        return PessoaRepository(self.db).criar(Pessoa(nome, email))

    def criar_compromisso(
        self,
        titulo="Reunião",
        descricao="Pauta da reunião",
        dias=1,
        pessoas=None,
    ):
        from models.compromisso import Compromisso
        from repositories.compromisso_repository import CompromissoRepository

        return CompromissoRepository(self.db).criar(
            Compromisso(
                data_horario=datetime.now() + timedelta(days=dias),
                titulo=titulo,
                descricao=descricao,
                pessoas=[str(pessoa.id) for pessoa in (pessoas or [])],
            )
        )
