from datetime import datetime

from bson import ObjectId


class CompromissoValidador:

    def __init__(self, dados_formulario, pessoa_repositorio):
        self.dados_brutos = dados_formulario or {}
        self.repositorio = pessoa_repositorio

        self.data_horario = self.dados_brutos.get("data_horario", "").strip()
        self.titulo = self.dados_brutos.get("titulo", "").strip()
        self.descricao = self.dados_brutos.get("descricao", "").strip()
        self.pessoas = self.dados_brutos.get("pessoas", []) or []

        self._data_horario_convertida = None
        self.erros = {}
        self._validar()

    def _validar(self):
        self._validar_titulo()
        self._validar_data_horario()
        self._validar_pessoas()

    def _validar_titulo(self):
        if not self.titulo:
            self.erros["titulo"] = "O título é obrigatório."

    def _validar_data_horario(self):
        if not self.data_horario:
            self.erros["data_horario"] = "A data e o horário são obrigatórios."
            return

        try:
            self._data_horario_convertida = datetime.fromisoformat(self.data_horario)
        except ValueError:
            self.erros["data_horario"] = "Digite uma data e um horário válidos."

    def _validar_pessoas(self):
        if not self.pessoas:
            self.erros["pessoas"] = "Selecione ao menos uma pessoa."
            return

        ids_validos = []
        for id_pessoa in self.pessoas:
            if not ObjectId.is_valid(id_pessoa):
                self.erros["pessoas"] = "Selecione pessoas válidas."
                return
            if id_pessoa not in ids_validos:
                ids_validos.append(id_pessoa)

        pessoas_encontradas = self.repositorio.buscar_por_ids(ids_validos)
        if len(pessoas_encontradas) != len(ids_validos):
            self.erros["pessoas"] = "Uma ou mais pessoas selecionadas não existem."

    def eh_valido(self) -> bool:
        return len(self.erros) == 0

    @property
    def dados_limpos(self) -> dict:
        return {
            "data_horario": self._data_horario_convertida,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "pessoas": self.pessoas,
        }
