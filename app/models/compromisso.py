from datetime import datetime

class Compromisso:
    def __init__(self, data_horario:datetime, titulo:str, descricao:str, pessoas:list[str], _id=None):
        self.id = str(_id) if _id else None
        self.data_horario = data_horario
        self.titulo = titulo.strip()
        self.descricao = descricao.strip()
        self.pessoas = pessoas

   

    def to_dict(self) -> dict: 

        return {
            "data_horario": self.data_horario,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "pessoas": self.pessoas
        }

    @classmethod
    def from_dict(cls, dados:dict|None):
        if not dados:
            return None

        return cls(
            _id=dados.get("_id"),
            data_horario=dados.get("data_horario"),
            titulo=dados.get("titulo",""),
            descricao=dados.get("descricao",""),
            pessoas=[str(p) for p in dados.get("pessoas", [])]
        )

