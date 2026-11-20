"""Testes estruturais do CSS separado e dos ajustes de formulário."""

import unittest

from base import DIRETORIO_APP


class TestAssets(unittest.TestCase):
    NOMES_CSS = [
        "tokens.css",
        "base.css",
        "formularios.css",
        "componentes.css",
        "responsivo.css",
    ]

    def test_base_carrega_os_css_na_ordem(self):
        html = (DIRETORIO_APP / "templates" / "base.html").read_text(
            encoding="utf-8"
        )
        posicoes = [html.find(f"css/{nome}") for nome in self.NOMES_CSS]

        self.assertTrue(all(posicao >= 0 for posicao in posicoes))
        self.assertEqual(posicoes, sorted(posicoes))
        self.assertNotIn('filename="style.css"', html)

    def test_arquivos_css_existem(self):
        for nome in self.NOMES_CSS:
            with self.subTest(css=nome):
                self.assertTrue(
                    (DIRETORIO_APP / "static" / "css" / nome).is_file()
                )

    def test_ajustes_de_formulario_estao_presentes(self):
        tokens = (DIRETORIO_APP / "static" / "css" / "tokens.css").read_text(
            encoding="utf-8"
        )
        formularios = (
            DIRETORIO_APP / "static" / "css" / "formularios.css"
        ).read_text(encoding="utf-8")

        self.assertIn("--largura-formulario", tokens)
        self.assertIn("input + .campo-ajuda", formularios)

    def test_acoes_do_card_de_pessoa_ficam_em_linha_propria(self):
        componentes = (
            DIRETORIO_APP / "static" / "css" / "componentes.css"
        ).read_text(encoding="utf-8")

        self.assertIn('"avatar dados"', componentes)
        self.assertIn('"acoes acoes"', componentes)
        self.assertIn("grid-area: acoes;", componentes)
        self.assertIn("grid-area: dados;", componentes)
