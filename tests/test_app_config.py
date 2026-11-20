"""Testes da inicialização da aplicação (configuração e blueprints)."""

import importlib.util
import os
from unittest.mock import patch

from base import DIRETORIO_APP, BancoFake, BaseTeste
from repositories.compromisso_repository import CompromissoRepository
from repositories.pessoa_repository import PessoaRepository


def carregar_modulo_app():
    especificacao = importlib.util.spec_from_file_location(
        "modulo_app_teste", DIRETORIO_APP / "app.py"
    )
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


class TestConfiguracaoApp(BaseTeste):
    def test_secret_key_e_blueprints(self):
        modulo = carregar_modulo_app()
        banco = BancoFake()
        cliente = {"agenda_teste": banco}
        ambiente = {
            "MONGO_URI": "mongodb://fake:27017",
            "MONGO_DATABASE": "agenda_teste",
            "SECRET_KEY": "chave-configurada",
        }

        with (
            patch.dict(os.environ, ambiente),
            patch.object(modulo, "MongoClient", return_value=cliente),
            patch.object(PessoaRepository, "garantir_indices"),
            patch.object(CompromissoRepository, "garantir_indices"),
        ):
            aplicacao = modulo.iniciar_app()

        self.assertEqual("chave-configurada", aplicacao.secret_key)
        self.assertIs(banco, aplicacao.db)
        rotas = {regra.rule for regra in aplicacao.url_map.iter_rules()}
        self.assertIn("/", rotas)
        self.assertIn("/pessoas", rotas)
        self.assertIn("/compromissos/<id>", rotas)

    def test_fallback_de_secret_key_para_desenvolvimento(self):
        modulo = carregar_modulo_app()
        banco = BancoFake()
        cliente = {"agenda_teste": banco}

        with (
            patch.dict(
                os.environ,
                {
                    "MONGO_URI": "mongodb://fake:27017",
                    "MONGO_DATABASE": "agenda_teste",
                },
                clear=True,
            ),
            patch.object(modulo, "MongoClient", return_value=cliente),
            patch.object(PessoaRepository, "garantir_indices"),
            patch.object(CompromissoRepository, "garantir_indices"),
        ):
            aplicacao = modulo.iniciar_app()

        self.assertEqual("dev-secret-alterar-em-producao", aplicacao.secret_key)
