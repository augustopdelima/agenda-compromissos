import re


class PessoaValidador:
    CAMPOS_EDICAO = ("nome", "email")

    def __init__(
        self,
        dados_formulario,
        pessoa_repositorio=None,
        modo="criacao",
        id_pessoa=None,
    ):
        self.dados_brutos = dados_formulario or {}
        self.repositorio = pessoa_repositorio
        self.modo = modo
        self.id_pessoa = str(id_pessoa) if id_pessoa else None

        self.erros = {}
        self._dados_limpos_edicao = {}
        self.nome = ""
        self.email = ""

        if modo == "criacao":
            self._validar_criacao()
        elif modo == "edicao":
            self._validar_edicao()
        else:
            raise ValueError(f"Modo de validação desconhecido: {modo}")

    # Regras individuais, compartilhadas pelos modos de validação
    def _erro_nome(self, nome: str) -> str | None:
        if not nome:
            return "O nome é obrigatório."
        if len(nome) < 2:
            return "O nome deve ter pelo menos 2 caracteres."
        return None

    def _erro_email(self, email: str) -> str | None:
        if not email:
            return "O e-mail é obrigatório."
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            return "Digite um endereço de e-mail válido."

        encontrada = self.repositorio.buscar_por_email(email) if self.repositorio else None
        if encontrada and encontrada.id != self.id_pessoa:
            return "Este e-mail já está cadastrado."
        return None

    # Criação: nome e e-mail obrigatórios e e-mail único
    def _validar_criacao(self):
        self.nome = self.dados_brutos.get("nome", "").strip()
        self.email = self.dados_brutos.get("email", "").strip().lower()

        mensagens = {
            "nome": self._erro_nome(self.nome),
            "email": self._erro_email(self.email),
        }
        self.erros = {
            campo: mensagem for campo, mensagem in mensagens.items() if mensagem
        }

    # Edição: valida apenas as chaves efetivamente enviadas
    def _validar_edicao(self):
        limpos = {}

        for campo in self.dados_brutos:
            if campo not in self.CAMPOS_EDICAO:
                self.erros[campo] = "Este campo não pode ser alterado."

        for campo in self.CAMPOS_EDICAO:
            if campo not in self.dados_brutos:
                continue

            valor = self.dados_brutos[campo].strip()
            if campo == "email":
                valor = valor.lower()

            mensagem = (
                self._erro_email(valor) if campo == "email" else self._erro_nome(valor)
            )
            if mensagem:
                self.erros[campo] = mensagem

            limpos[campo] = valor

        if not self.erros and not limpos:
            self.erros["geral"] = "Informe ao menos um campo para editar."

        self._dados_limpos_edicao = limpos

    def eh_valido(self) -> bool:
        return len(self.erros) == 0

    @property
    def dados_limpos(self) -> dict:
        if self.modo == "edicao":
            return self._dados_limpos_edicao

        return {
            "nome": self.nome,
            "email": self.email,
        }
