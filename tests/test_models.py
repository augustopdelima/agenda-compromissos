"""Testes das entidades de domínio."""

from datetime import datetime

from bson import ObjectId

from base import BaseTeste
from models.compromisso import Compromisso
from models.pessoa import Pessoa


class TestPessoa(BaseTeste):
    def test_criacao_remove_espacos_e_converte_id(self):
        identificador = ObjectId()
        pessoa = Pessoa("  Ana Lima  ", " ANA@Exemplo.com ", _id=identificador)

        self.assertEqual(str(identificador), pessoa.id)
        self.assertEqual("Ana Lima", pessoa.nome)
        self.assertEqual("ANA@Exemplo.com", pessoa.email)

    def test_sem_id_quando_nao_informado(self):
        self.assertIsNone(Pessoa("Ana", "ana@exemplo.com").id)

    def test_to_dict_nao_inclui_id(self):
        pessoa = Pessoa("Ana", "ana@exemplo.com", _id=ObjectId())

        self.assertEqual({"nome": "Ana", "email": "ana@exemplo.com"}, pessoa.to_dict())

    def test_from_dict(self):
        identificador = ObjectId()
        pessoa = Pessoa.from_dict(
            {"_id": identificador, "nome": "Ana", "email": "ana@exemplo.com"}
        )

        self.assertEqual(str(identificador), pessoa.id)
        self.assertEqual("Ana", pessoa.nome)
        self.assertEqual("ana@exemplo.com", pessoa.email)

    def test_from_dict_com_dados_vazios(self):
        self.assertIsNone(Pessoa.from_dict(None))
        self.assertIsNone(Pessoa.from_dict({}))


class TestCompromisso(BaseTeste):
    def test_criacao_remove_espacos_e_converte_id(self):
        identificador = ObjectId()
        data = datetime(2030, 5, 10, 14, 30)
        compromisso = Compromisso(
            data, "  Reunião  ", "  Pauta  ", ["id-1"], _id=identificador
        )

        self.assertEqual(str(identificador), compromisso.id)
        self.assertEqual("Reunião", compromisso.titulo)
        self.assertEqual("Pauta", compromisso.descricao)
        self.assertEqual(["id-1"], compromisso.pessoas)
        self.assertEqual(data, compromisso.data_horario)

    def test_to_dict(self):
        data = datetime(2030, 5, 10, 14, 30)
        compromisso = Compromisso(data, "Reunião", "Pauta", ["id-1"])

        self.assertEqual(
            {
                "data_horario": data,
                "titulo": "Reunião",
                "descricao": "Pauta",
                "pessoas": ["id-1"],
            },
            compromisso.to_dict(),
        )

    def test_from_dict_converte_ids_de_pessoas_para_string(self):
        ids = [ObjectId(), ObjectId()]
        compromisso = Compromisso.from_dict(
            {
                "_id": ObjectId(),
                "data_horario": datetime(2030, 5, 10, 14, 30),
                "titulo": "Reunião",
                "pessoas": ids,
            }
        )

        self.assertEqual([str(id_) for id_ in ids], compromisso.pessoas)
        self.assertEqual("", compromisso.descricao)

    def test_from_dict_com_dados_vazios(self):
        self.assertIsNone(Compromisso.from_dict(None))
        self.assertIsNone(Compromisso.from_dict({}))
