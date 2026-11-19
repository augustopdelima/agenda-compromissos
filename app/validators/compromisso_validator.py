from datetime import datetime

from bson import ObjectId


class CompromissoValidador:
    CAMPOS_EDICAO = ("titulo", "descricao")

    def __init__(self, dados_formulario, pessoa_repositorio=None, modo="criacao"):
        self.dados_brutos = dados_formulario or {}
        self.repositorio = pessoa_repositorio
        self.modo = modo

        self.erros = {}
        self._data_horario_convertida = None
        self._dados_limpos_edicao = {}

        if modo == "criacao":
            self._validar_criacao()
        elif modo == "edicao":
            self._validar_edicao()
        else:
            raise ValueError(f"Modo de validação desconhecido: {modo}")

    # Regras individuais, compartilhadas pelos dois cenários
    def _erro_titulo(self, titulo: str) -> str | None:
        if not titulo:
            return "O título é obrigatório."
        return None

    def _validar_data_horario(self, data_horario: str) -> str | None:
        if not data_horario:
            return "A data e o horário são obrigatórios."

        try:
            self._data_horario_convertida = datetime.fromisoformat(data_horario)
        except ValueError:
            return "Digite uma data e um horário válidos."
        return None

    def _validar_pessoas(self, pessoas: list) -> str | None:
        if not pessoas:
            return "Selecione ao menos uma pessoa."

        ids_validos = []
        for id_pessoa in pessoas:
            if not ObjectId.is_valid(id_pessoa):
                return "Selecione pessoas válidas."
            if id_pessoa not in ids_validos:
                ids_validos.append(id_pessoa)

        pessoas_encontradas = self.repositorio.buscar_por_ids(ids_validos)
        if len(pessoas_encontradas) != len(ids_validos):
            return "Uma ou mais pessoas selecionadas não existem."
        return None

    # Criação: continua exigindo todos os campos, com as mesmas mensagens
    def _validar_criacao(self):
        self.data_horario = self.dados_brutos.get("data_horario", "").strip()
        self.titulo = self.dados_brutos.get("titulo", "").strip()
        self.descricao = self.dados_brutos.get("descricao", "").strip()
        self.pessoas = self.dados_brutos.get("pessoas", []) or []

        mensagens = {
            "titulo": self._erro_titulo(self.titulo),
            "data_horario": self._validar_data_horario(self.data_horario),
            "pessoas": self._validar_pessoas(self.pessoas),
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
            if campo == "titulo":
                mensagem = self._erro_titulo(valor)
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
            "data_horario": self._data_horario_convertida,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "pessoas": self.pessoas,
        }
