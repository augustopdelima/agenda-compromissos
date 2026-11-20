"""Testes das operações de escrita dos repositories."""

from datetime import datetime, timedelta

from base import BaseTeste
from models.compromisso import Compromisso
from models.pessoa import Pessoa
from repositories.compromisso_repository import CompromissoRepository
from repositories.pessoa_repository import PessoaRepository


class TestRemocaoDeReferencias(BaseTeste):
    def setUp(self):
        super().setUp()
        self.pessoas = PessoaRepository(self.db)
        self.compromissos = CompromissoRepository(self.db)

    def test_remove_id_de_todos_os_compromissos(self):
        ana = self.pessoas.criar(Pessoa("Ana", "ana@exemplo.com"))
        bruno = self.pessoas.criar(Pessoa("Bruno", "bruno@exemplo.com"))
        base = datetime(2030, 1, 1)
        self.compromissos.criar(Compromisso(base, "A", "", [ana.id, bruno.id]))
        self.compromissos.criar(
            Compromisso(base + timedelta(days=1), "B", "", [ana.id])
        )
        self.compromissos.criar(
            Compromisso(base + timedelta(days=2), "C", "", [bruno.id])
        )

        afetados = self.compromissos.remover_pessoa_dos_compromissos(ana.id)

        self.assertEqual(2, afetados)
        self.assertEqual(
            [[bruno.id], [], [bruno.id]],
            [compromisso.pessoas for compromisso in self.compromissos.buscar_todos()],
        )

    def test_operacao_e_idempotente(self):
        ana = self.pessoas.criar(Pessoa("Ana", "ana@exemplo.com"))
        self.compromissos.criar(
            Compromisso(datetime(2030, 1, 1), "A", "", [ana.id])
        )

        self.assertEqual(1, self.compromissos.remover_pessoa_dos_compromissos(ana.id))
        self.assertEqual(0, self.compromissos.remover_pessoa_dos_compromissos(ana.id))

    def test_id_invalido_nao_afeta_os_compromissos(self):
        ana = self.pessoas.criar(Pessoa("Ana", "ana@exemplo.com"))
        self.compromissos.criar(
            Compromisso(datetime(2030, 1, 1), "A", "", [ana.id])
        )

        self.assertEqual(0, self.compromissos.remover_pessoa_dos_compromissos("invalido"))
        self.assertEqual([ana.id], self.compromissos.buscar_todos()[0].pessoas)

    def test_excluir_pessoa_nao_apaga_compromissos(self):
        ana = self.pessoas.criar(Pessoa("Ana", "ana@exemplo.com"))
        self.compromissos.criar(
            Compromisso(datetime(2030, 1, 1), "A", "", [ana.id])
        )

        self.assertTrue(self.pessoas.excluir(ana.id))
        self.assertEqual(0, len(self.pessoas.buscar_todos()))
        self.assertEqual(1, len(self.compromissos.buscar_todos()))
