"""Testes das regras de validação de pessoas e compromissos."""

from datetime import datetime
from bson import ObjectId

from base import BaseTeste
from models.pessoa import Pessoa
from repositories.compromisso_repository import CompromissoRepository
from repositories.pessoa_repository import PessoaRepository
from validators.compromisso_validator import CompromissoValidador
from validators.pessoa_validator import PessoaValidador


class TestPessoaValidador(BaseTeste):
    def setUp(self):
        super().setUp()
        self.repositorio = PessoaRepository(self.db)

    def test_dados_validos_sao_normalizados(self):
        validador = PessoaValidador(
            {"nome": "  Ana Lima  ", "email": " ANA@Exemplo.com "},
            self.repositorio,
        )

        self.assertTrue(validador.eh_valido())
        self.assertEqual({}, validador.erros)
        self.assertEqual(
            {"nome": "Ana Lima", "email": "ana@exemplo.com"},
            validador.dados_limpos,
        )

    def test_nome_obrigatorio_e_tamanho_minimo(self):
        sem_nome = PessoaValidador({"nome": "", "email": "ana@exemplo.com"}, self.repositorio)
        curto = PessoaValidador({"nome": "A", "email": "ana@exemplo.com"}, self.repositorio)

        self.assertEqual("O nome é obrigatório.", sem_nome.erros["nome"])
        self.assertEqual("O nome deve ter pelo menos 2 caracteres.", curto.erros["nome"])

    def test_email_obrigatorio_e_formato(self):
        vazio = PessoaValidador({"nome": "Ana", "email": ""}, self.repositorio)
        invalido = PessoaValidador({"nome": "Ana", "email": "ana-sem-arroba"}, self.repositorio)

        self.assertEqual("O e-mail é obrigatório.", vazio.erros["email"])
        self.assertEqual("Digite um endereço de e-mail válido.", invalido.erros["email"])

    def test_email_duplicado(self):
        self.repositorio.criar(Pessoa("Ana", "ana@exemplo.com"))
        validador = PessoaValidador(
            {"nome": "Outra Ana", "email": "ANA@exemplo.com"}, self.repositorio
        )

        self.assertFalse(validador.eh_valido())
        self.assertEqual("Este e-mail já está cadastrado.", validador.erros["email"])


class TestCompromissoValidador(BaseTeste):
    def setUp(self):
        super().setUp()
        self.repositorio_pessoas = PessoaRepository(self.db)
        self.repositorio_compromissos = CompromissoRepository(self.db)
        self.pessoa = self.repositorio_pessoas.criar(Pessoa("Ana", "ana@exemplo.com"))
        self.id_pessoa = str(self.pessoa.id)

    def test_criacao_valida_com_pessoas(self):
        validador = CompromissoValidador(
            {
                "data_horario": "2030-05-10T14:30",
                "titulo": "  Reunião  ",
                "descricao": "  Pauta  ",
                "pessoas": [self.id_pessoa],
            },
            self.repositorio_pessoas,
        )

        self.assertTrue(validador.eh_valido())
        dados = validador.dados_limpos
        self.assertEqual(datetime(2030, 5, 10, 14, 30), dados["data_horario"])
        self.assertEqual("Reunião", dados["titulo"])
        self.assertEqual("Pauta", dados["descricao"])
        self.assertEqual([self.id_pessoa], dados["pessoas"])

    def test_criacao_sem_pessoas_e_permitida(self):
        validador = CompromissoValidador(
            {"data_horario": "2030-05-10T14:30", "titulo": "Sem gente"},
            self.repositorio_pessoas,
        )

        self.assertTrue(validador.eh_valido())
        self.assertEqual([], validador.dados_limpos["pessoas"])

    def test_criacao_exige_titulo_e_data(self):
        validador = CompromissoValidador({}, self.repositorio_pessoas)

        self.assertFalse(validador.eh_valido())
        self.assertEqual("O título é obrigatório.", validador.erros["titulo"])
        self.assertEqual("A data e o horário são obrigatórios.", validador.erros["data_horario"])

    def test_criacao_rejeita_data_invalida(self):
        validador = CompromissoValidador(
            {"data_horario": "data-qualquer", "titulo": "Reunião"},
            self.repositorio_pessoas,
        )

        self.assertEqual("Digite uma data e um horário válidos.", validador.erros["data_horario"])

    def test_criacao_rejeita_ids_invalidos_e_inexistentes(self):
        invalido = CompromissoValidador(
            {"data_horario": "2030-05-10T14:30", "titulo": "Reunião", "pessoas": ["abc"]},
            self.repositorio_pessoas,
        )
        inexistente = CompromissoValidador(
            {
                "data_horario": "2030-05-10T14:30",
                "titulo": "Reunião",
                "pessoas": [str(ObjectId())],
            },
            self.repositorio_pessoas,
        )

        self.assertEqual("Selecione pessoas válidas.", invalido.erros["pessoas"])
        self.assertEqual("Uma ou mais pessoas selecionadas não existem.", inexistente.erros["pessoas"])

    def test_edicao_aceita_apenas_campos_permitidos(self):
        validador = CompromissoValidador(
            {"titulo": "  Novo título  ", "descricao": "  Nova descrição  "},
            modo="edicao",
        )

        self.assertTrue(validador.eh_valido())
        self.assertEqual(
            {"titulo": "Novo título", "descricao": "Nova descrição"},
            validador.dados_limpos,
        )

    def test_edicao_rejeita_titulo_vazio_e_campos_extras(self):
        validador = CompromissoValidador(
            {"titulo": "   ", "pessoas": [self.id_pessoa]}, modo="edicao"
        )

        self.assertFalse(validador.eh_valido())
        self.assertEqual("O título é obrigatório.", validador.erros["titulo"])
        self.assertEqual("Este campo não pode ser alterado.", validador.erros["pessoas"])

    def test_edicao_sem_campos(self):
        validador = CompromissoValidador({}, modo="edicao")

        self.assertEqual("Informe ao menos um campo para editar.", validador.erros["geral"])

    def test_pessoas_vinculadas_aceita_lista_vazia_e_remove_duplicatas(self):
        vazio = CompromissoValidador({"pessoas": []}, self.repositorio_pessoas, modo="pessoas")
        duplicatas = CompromissoValidador(
            {"pessoas": [self.id_pessoa, self.id_pessoa]},
            self.repositorio_pessoas,
            modo="pessoas",
        )

        self.assertTrue(vazio.eh_valido())
        self.assertEqual({"pessoas": []}, vazio.dados_limpos)
        self.assertTrue(duplicatas.eh_valido())
        self.assertEqual({"pessoas": [self.id_pessoa]}, duplicatas.dados_limpos)

    def test_modo_desconhecido(self):
        with self.assertRaises(ValueError):
            CompromissoValidador({}, modo="inexistente")
