"""Testes das funções auxiliares extraídas dos controllers."""

from datetime import datetime, timedelta

from bson import ObjectId
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import NotFound

from base import BaseTeste
from helpers.compromissos import montar_compromissos_com_pessoas
from helpers.formulario import (
    obter_dados_edicao,
    obter_dados_formulario,
    obter_url_cancelar,
    obter_url_retorno,
    url_interna_segura,
)
from helpers.periodo import (
    PERIODOS,
    filtrar_compromissos_por_periodo,
    obter_periodo,
)
from helpers.repositorios import obter_compromisso_ou_404, obter_pessoa_ou_404
from models.compromisso import Compromisso


class TestPeriodo(BaseTeste):
    def test_obter_periodo(self):
        with self.app.test_request_context("/?periodo=proximos"):
            self.assertEqual("proximos", obter_periodo())
        with self.app.test_request_context("/"):
            self.assertEqual("todos", obter_periodo())
        with self.app.test_request_context("/?periodo=inexistente"):
            self.assertEqual("todos", obter_periodo())

    def test_periodos_conhecidos(self):
        self.assertEqual(
            {
                "proximos": "Futuros compromissos",
                "passados": "Compromissos antigos",
                "todos": "Todos os compromissos",
            },
            PERIODOS,
        )

    def test_filtragem(self):
        agora = datetime.now()
        passado = Compromisso(agora - timedelta(days=1), "Passado", "", [])
        futuro = Compromisso(agora + timedelta(days=1), "Futuro", "", [])
        todos = [passado, futuro]

        self.assertEqual(todos, filtrar_compromissos_por_periodo(todos, "todos"))
        self.assertEqual([futuro], filtrar_compromissos_por_periodo(todos, "proximos"))
        self.assertEqual([passado], filtrar_compromissos_por_periodo(todos, "passados"))


class TestFormulario(BaseTeste):
    URL_ATUAL = "/compromissos/abc/editar"

    def test_url_interna_segura(self):
        with self.app.test_request_context(self.URL_ATUAL, method="POST"):
            self.assertEqual(
                "http://localhost/compromissos/",
                url_interna_segura("http://localhost/compromissos/", "/fallback"),
            )
            self.assertEqual("/fallback", url_interna_segura("http://externo.com/", "/fallback"))
            self.assertEqual("/fallback", url_interna_segura(self.URL_ATUAL, "/fallback"))
            self.assertEqual("/fallback", url_interna_segura(None, "/fallback"))

    def test_obter_url_cancelar_usa_referrer(self):
        referrer = "http://localhost/?periodo=passados"
        with self.app.test_request_context(
            self.URL_ATUAL, headers={"Referer": referrer}
        ):
            self.assertEqual(referrer, obter_url_cancelar("/fallback"))
        with self.app.test_request_context(self.URL_ATUAL):
            self.assertEqual("/fallback", obter_url_cancelar("/fallback"))

    def test_obter_url_retorno_usa_formulario(self):
        retorno = "http://localhost/compromissos/abc"
        with self.app.test_request_context(
            self.URL_ATUAL, method="POST", data={"url_retorno": retorno}
        ):
            self.assertEqual(retorno, obter_url_retorno("/fallback"))
        with self.app.test_request_context(self.URL_ATUAL, method="POST"):
            self.assertEqual("/fallback", obter_url_retorno("/fallback"))

    def test_leitura_dos_dados_do_formulario(self):
        dados = MultiDict(
            [
                ("data_horario", "2030-05-10T14:30"),
                ("titulo", "Reunião"),
                ("descricao", "Pauta"),
                ("pessoas", "id-1"),
                ("pessoas", "id-2"),
                ("url_retorno", "http://localhost/"),
            ]
        )
        with self.app.test_request_context("/", method="POST", data=dados):
            self.assertEqual(
                {
                    "data_horario": "2030-05-10T14:30",
                    "titulo": "Reunião",
                    "descricao": "Pauta",
                    "pessoas": ["id-1", "id-2"],
                },
                obter_dados_formulario(),
            )
            self.assertEqual(
                {"titulo": "Reunião", "descricao": "Pauta"},
                obter_dados_edicao(),
            )

    def test_obter_dados_edicao_aceita_campos_customizados(self):
        dados = MultiDict(
            [
                ("nome", "Ana Lima"),
                ("email", "ana@exemplo.com"),
                ("url_retorno", "http://localhost/pessoas"),
            ]
        )
        with self.app.test_request_context("/pessoas/abc/editar", method="POST", data=dados):
            self.assertEqual(
                {"nome": "Ana Lima", "email": "ana@exemplo.com"},
                obter_dados_edicao(("nome", "email")),
            )


class TestCompromissosHelper(BaseTeste):
    def test_agrupa_pessoas_e_ignora_ids_que_nao_existem(self):
        ana = self.criar_pessoa("Ana", "ana@exemplo.com")
        bruno = self.criar_pessoa("Bruno", "bruno@exemplo.com")
        compromisso = self.criar_compromisso(
            titulo="Reunião", pessoas=[ana, bruno]
        )
        compromisso.pessoas = [ana.id, str(ObjectId()), bruno.id]

        with self.app.test_request_context("/"):
            resultado = montar_compromissos_com_pessoas([compromisso])

        self.assertEqual(1, len(resultado))
        self.assertEqual(compromisso, resultado[0]["compromisso"])
        self.assertEqual(["Ana", "Bruno"], [p.nome for p in resultado[0]["pessoas"]])

    def test_lista_vazia(self):
        with self.app.test_request_context("/"):
            self.assertEqual([], montar_compromissos_com_pessoas([]))


class TestRepositoriosHelper(BaseTeste):
    def test_obter_compromisso_ou_404(self):
        compromisso = self.criar_compromisso()

        with self.app.test_request_context("/"):
            self.assertEqual(compromisso.id, obter_compromisso_ou_404(compromisso.id).id)

        with self.app.test_request_context("/"):
            with self.assertRaises(NotFound):
                obter_compromisso_ou_404("id-invalido")

        with self.app.test_request_context("/"):
            with self.assertRaises(NotFound):
                obter_compromisso_ou_404(str(ObjectId()))

    def test_obter_pessoa_ou_404(self):
        pessoa = self.criar_pessoa()

        with self.app.test_request_context("/"):
            self.assertEqual(pessoa.id, obter_pessoa_ou_404(pessoa.id).id)

        with self.app.test_request_context("/"):
            with self.assertRaises(NotFound):
                obter_pessoa_ou_404("id-invalido")

        with self.app.test_request_context("/"):
            with self.assertRaises(NotFound):
                obter_pessoa_ou_404(str(ObjectId()))
