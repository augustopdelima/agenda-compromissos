"""Testes de integração das rotas e dos templates renderizados."""

from urllib.parse import urlparse

from base import BaseTeste


class BaseRotasTeste(BaseTeste):
    @staticmethod
    def caminho(resposta):
        return urlparse(resposta.headers.get("Location", "")).path

    def post(self, url, dados=None, **kwargs):
        return self.cliente.post(url, data=dados or {}, **kwargs)


class TestHome(BaseRotasTeste):
    def test_visao_geral(self):
        resposta = self.cliente.get("/")

        self.assertEqual(200, resposta.status_code)
        html = self.html(resposta)
        self.assertIn("Visão geral", html)
        self.assertIn('class="resumo"', html)
        self.assertIn("Próximos 7 dias", html)
        self.assertIn("Total de compromissos", html)
        self.assertIn("Sem pessoas vinculadas", html)
        self.assertIn('class="skip-link"', html)
        self.assertIn("Todos os compromissos", html)

    def test_filtros_e_fallback(self):
        futuro = self.criar_compromisso("Futuro", dias=2)
        passado = self.criar_compromisso("Antigo", dias=-2)

        html_futuros = self.html(self.cliente.get("/?periodo=proximos"))
        self.assertIn("Futuros compromissos", html_futuros)
        self.assertIn(futuro.titulo, html_futuros)
        self.assertNotIn(f'title="{passado.titulo}"', html_futuros)

        html_antigos = self.html(self.cliente.get("/?periodo=passados"))
        self.assertIn("Compromissos antigos", html_antigos)
        self.assertIn(passado.titulo, html_antigos)
        self.assertNotIn(f'title="{futuro.titulo}"', html_antigos)

        html_todos = self.html(self.cliente.get("/?periodo=invalido"))
        self.assertIn("Todos os compromissos", html_todos)
        self.assertIn("Futuro", html_todos)
        self.assertIn("Antigo", html_todos)

    def test_filtro_marca_opcao_ativa(self):
        html = self.html(self.cliente.get("/"))

        self.assertIn('class="filtro ativo"', html)
        self.assertIn('aria-current="page"', html)
        self.assertIn("Futuros", html)
        self.assertIn("Antigos", html)

    def test_resumo_da_agenda(self):
        ana = self.criar_pessoa("Ana", "ana@exemplo.com")
        self.criar_compromisso("Perto", dias=2, pessoas=[ana])
        self.criar_compromisso("Longe", dias=30)
        self.criar_compromisso("Passado", dias=-1)

        html = self.html(self.cliente.get("/"))

        self.assertIn('<span class="resumo-card__valor">1</span>', html)  # até 7 dias
        self.assertIn('<span class="resumo-card__valor">3</span>', html)  # total
        self.assertIn('<span class="resumo-card__valor">2</span>', html)  # sem pessoas


class TestCompromissos(BaseRotasTeste):
    def test_listagem_com_formulario_recolhido_e_acoes(self):
        self.criar_compromisso("Reunião", "Detalhes da pauta")

        resposta = self.cliente.get("/compromissos")
        html = self.html(resposta)

        self.assertEqual(200, resposta.status_code)
        self.assertIn('<details class="formulario-colapsavel" id="novo-compromisso"', html)
        self.assertIn("Novo compromisso", html)
        self.assertIn("compromisso-card__link", html)
        self.assertIn("Gerenciar pessoas", html)
        self.assertIn('data-abrir-dialog="', html)
        self.assertIn('aria-haspopup="dialog"', html)

    def test_texto_de_ajuda_fica_depois_do_input(self):
        html = self.html(self.cliente.get("/compromissos"))

        posicao_input = html.find('id="data_horario"')
        posicao_ajuda = html.find('id="data_horario-ajuda"')

        self.assertGreater(posicao_input, -1)
        self.assertGreater(posicao_ajuda, posicao_input)

    def test_criar_compromisso_com_sucesso(self):
        pessoa = self.criar_pessoa("Ana", "ana@exemplo.com")
        resposta = self.post(
            "/compromissos/criar",
            {
                "data_horario": "2030-05-10T14:30",
                "titulo": "  Reunião  ",
                "descricao": "  Pauta  ",
                "pessoas": pessoa.id,
            },
        )

        self.assertEqual(302, resposta.status_code)
        self.assertEqual("/compromissos/", self.caminho(resposta))
        documentos = self.db["compromissos"].documentos
        self.assertEqual(1, len(documentos))
        self.assertEqual("Reunião", documentos[0]["titulo"])
        self.assertEqual("Pauta", documentos[0]["descricao"])
        self.assertEqual([pessoa.id], documentos[0]["pessoas"])

        html = self.html(self.cliente.get("/compromissos/"))
        self.assertIn("Compromisso cadastrado com sucesso.", html)
        self.assertIn("Reunião", html)

    def test_criar_compromisso_invalido(self):
        resposta = self.post("/compromissos/criar", {"titulo": "", "data_horario": ""})

        self.assertEqual(400, resposta.status_code)
        html = self.html(resposta)
        self.assertIn("Não foi possível cadastrar.", html)
        self.assertIn("O título é obrigatório.", html)
        self.assertIn('id="novo-compromisso" open', html)
        self.assertEqual(0, len(self.db["compromissos"].documentos))

    def test_detalhes(self):
        ana = self.criar_pessoa("Ana", "ana@exemplo.com")
        bruno = self.criar_pessoa("Bruno", "bruno@exemplo.com")
        compromisso = self.criar_compromisso(
            "Reunião", "Pauta da reunião", pessoas=[ana, bruno]
        )

        resposta = self.cliente.get(f"/compromissos/{compromisso.id}")
        html = self.html(resposta)

        self.assertEqual(200, resposta.status_code)
        self.assertIn("Reunião", html)
        self.assertIn("Pauta da reunião", html)
        self.assertIn("Pessoas envolvidas (2)", html)
        self.assertIn("Ana", html)
        self.assertIn("bruno@exemplo.com", html)
        self.assertIn("Voltar aos compromissos", html)
        self.assertIn(f'id="excluir-detalhes-{compromisso.id}"', html)

    def test_detalhes_inexistente(self):
        resposta = self.cliente.get("/compromissos/id-invalido")

        self.assertEqual(404, resposta.status_code)
        self.assertIn("404 — Página não encontrada", self.html(resposta))

    def test_editar_get_usa_referrer_como_origem(self):
        compromisso = self.criar_compromisso()
        origem = "http://localhost/?periodo=passados"

        resposta = self.cliente.get(
            f"/compromissos/{compromisso.id}/editar",
            headers={"Referer": origem},
        )
        html = self.html(resposta)

        self.assertEqual(200, resposta.status_code)
        self.assertIn("Alterar título e descrição", html)
        self.assertIn(f'name="url_retorno" value="{origem}"', html)
        self.assertIn(f'href="{origem}"', html)

    def test_editar_post_retorna_a_origem(self):
        compromisso = self.criar_compromisso(titulo="Antigo", descricao="Antiga")
        origem = "http://localhost/?periodo=passados"

        resposta = self.post(
            f"/compromissos/{compromisso.id}/editar",
            {
                "titulo": "Novo título",
                "descricao": "Nova descrição",
                "url_retorno": origem,
            },
        )

        self.assertEqual(302, resposta.status_code)
        self.assertEqual(origem, resposta.headers["Location"])
        documento = self.db["compromissos"].documentos[0]
        self.assertEqual("Novo título", documento["titulo"])
        self.assertEqual("Nova descrição", documento["descricao"])
        self.assertIn(
            "Compromisso atualizado com sucesso.",
            self.html(self.cliente.get(origem)),
        )

    def test_editar_post_fallback_para_detalhes(self):
        compromisso = self.criar_compromisso()
        url = f"/compromissos/{compromisso.id}/editar"
        esperado = f"/compromissos/{compromisso.id}"

        externa = self.post(
            url,
            {"titulo": "Ok", "url_retorno": "http://externo.com/"},
        )
        mesma_pagina = self.post(
            url,
            {"titulo": "Ok", "url_retorno": f"http://localhost{url}"},
        )

        self.assertEqual(esperado, self.caminho(externa))
        self.assertEqual(esperado, self.caminho(mesma_pagina))

    def test_editar_post_invalido_preserva_origem(self):
        compromisso = self.criar_compromisso()
        origem = "http://localhost/?periodo=passados"

        resposta = self.post(
            f"/compromissos/{compromisso.id}/editar",
            {"titulo": "", "url_retorno": origem},
        )
        html = self.html(resposta)

        self.assertEqual(400, resposta.status_code)
        self.assertIn("Não foi possível salvar.", html)
        self.assertIn("O título é obrigatório.", html)
        self.assertIn(f'name="url_retorno" value="{origem}"', html)
        self.assertEqual("Reunião", self.db["compromissos"].documentos[0]["titulo"])

    def test_gerenciar_pessoas_salva_e_retorna_a_origem(self):
        ana = self.criar_pessoa("Ana", "ana@exemplo.com")
        bruno = self.criar_pessoa("Bruno", "bruno@exemplo.com")
        compromisso = self.criar_compromisso(pessoas=[ana, bruno])
        detalhes = f"http://localhost/compromissos/{compromisso.id}"

        resposta = self.post(
            f"/compromissos/{compromisso.id}/pessoas",
            {"url_retorno": detalhes},
        )

        self.assertEqual(302, resposta.status_code)
        self.assertEqual(detalhes, resposta.headers["Location"])
        self.assertEqual([], self.db["compromissos"].documentos[0]["pessoas"])
        self.assertIn(
            "Pessoas envolvidas atualizadas com sucesso.",
            self.html(self.cliente.get(detalhes)),
        )

    def test_gerenciar_pessoas_rejeita_id_invalido(self):
        compromisso = self.criar_compromisso()

        resposta = self.post(
            f"/compromissos/{compromisso.id}/pessoas",
            {"pessoas": "id-invalido"},
        )

        self.assertEqual(400, resposta.status_code)
        self.assertIn("Selecione pessoas válidas.", self.html(resposta))
        self.assertEqual([], self.db["compromissos"].documentos[0]["pessoas"])

    def test_excluir(self):
        compromisso = self.criar_compromisso()

        resposta = self.post(f"/compromissos/{compromisso.id}/excluir")

        self.assertEqual(302, resposta.status_code)
        self.assertEqual("/compromissos/", self.caminho(resposta))
        self.assertEqual(0, len(self.db["compromissos"].documentos))
        self.assertIn(
            "Compromisso excluído com sucesso.",
            self.html(self.cliente.get("/compromissos/")),
        )

    def test_card_limita_pessoas_e_mostra_excedente(self):
        pessoas = [
            self.criar_pessoa(f"Pessoa {i}", f"pessoa{i}@exemplo.com")
            for i in range(4)
        ]
        self.criar_compromisso("Com várias pessoas", pessoas=pessoas)

        html = self.html(self.cliente.get("/compromissos"))

        self.assertEqual(3, html.count('class="compromisso-card__pessoa"'))
        self.assertIn("+1", html)

    def test_estado_vazio_com_atalho(self):
        html = self.html(self.cliente.get("/compromissos"))

        self.assertIn("Nenhum compromisso cadastrado neste período.", html)
        self.assertIn("/compromissos/#novo-compromisso", html)


class TestPessoas(BaseRotasTeste):
    def test_listagem_com_formulario_recolhido(self):
        html = self.html(self.cliente.get("/pessoas"))

        self.assertIn('<details class="formulario-colapsavel" id="nova-pessoa"', html)
        self.assertIn("Nova pessoa", html)

    def test_criar_com_sucesso(self):
        resposta = self.post(
            "/pessoas/criar",
            {"nome": "  Ana Lima  ", "email": " ANA@Exemplo.com "},
        )

        self.assertEqual(302, resposta.status_code)
        self.assertEqual("/pessoas", self.caminho(resposta))
        documento = self.db["pessoas"].documentos[0]
        self.assertEqual("Ana Lima", documento["nome"])
        self.assertEqual("ana@exemplo.com", documento["email"])
        self.assertIn("Pessoa cadastrada com sucesso.", self.html(self.cliente.get("/pessoas")))

    def test_criar_invalido(self):
        resposta = self.post("/pessoas/criar", {"nome": "", "email": "invalido"})

        self.assertEqual(400, resposta.status_code)
        html = self.html(resposta)
        self.assertIn("O nome é obrigatório.", html)
        self.assertIn("Digite um endereço de e-mail válido.", html)
        self.assertIn('id="nova-pessoa" open', html)
        self.assertEqual(0, len(self.db["pessoas"].documentos))

    def test_email_duplicado(self):
        self.criar_pessoa("Ana", "ana@exemplo.com")

        resposta = self.post(
            "/pessoas/criar", {"nome": "Outra Ana", "email": "ana@exemplo.com"}
        )

        self.assertEqual(400, resposta.status_code)
        self.assertIn("Este e-mail já está cadastrado.", self.html(resposta))

    def test_estado_vazio_com_atalho(self):
        html = self.html(self.cliente.get("/pessoas"))

        self.assertIn("Nenhuma pessoa cadastrada ainda.", html)
        self.assertIn("/pessoas#nova-pessoa", html)
