import re

class PessoaValidador:

    def __init__(self, dados_formulario, pessoa_repositorio):
        self.dados_brutos = dados_formulario or {}
        self.repositorio = pessoa_repositorio

        self.nome = self.dados_brutos.get("nome", "").strip()
        self.email = self.dados_brutos.get("email", "").strip().lower() 

        self.erros = {}
        self._validar()

    def _validar(self):
        self._validar_nome()
        self._validar_email() 

    def _validar_nome(self):
        if not self.nome:
            self.erros["nome"] = "O nome é obrigatório."
        elif len(self.nome) < 2:
            self.erros["nome"] = "O nome deve ter pelo menos 2 caracteres."

    def _validar_email(self):
        if not self.email:
            self.erros["email"] = "O e-mail é obrigatório."
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", self.email):
            self.erros["email"] = "Digite um endereço de e-mail válido."
        elif self.repositorio.buscar_por_email(self.email):
            self.erros["email"] = "Este e-mail já está cadastrado."
 
    def eh_valido(self) -> bool:
        return len(self.erros) == 0

    @property
    def dados_limpos(self) -> dict:
        return {
            "nome": self.nome,
            "email": self.email, 
        }
