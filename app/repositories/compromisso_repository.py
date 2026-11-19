from models.compromisso import Compromisso
from datetime import datetime
from bson import ObjectId

class CompromissoRepository:
    def __init__(self, db):
        self.colecao = db["compromissos"]

    def garantir_indices(self):
        self.colecao.create_index("data_horario")

    def criar(self, compromisso: Compromisso) -> Compromisso:
        resultado = self.colecao.insert_one(compromisso.to_dict())
        
        compromisso.id = str(resultado.inserted_id)
        return compromisso

    def buscar_todos(self) -> list[Compromisso]:
        cursor = self.colecao.find().sort("data_horario", 1)
        return [Compromisso.from_dict(doc) for doc in cursor]

    def buscar_por_id(self, id: str) -> Compromisso | None:
        if not ObjectId.is_valid(id):
            return None

        documento = self.colecao.find_one({"_id": ObjectId(id)})
        return Compromisso.from_dict(documento)

    def atualizar_titulo_descricao(self, id: str, dados: dict) -> bool:
        if not ObjectId.is_valid(id) or not dados:
            return False

        resultado = self.colecao.update_one(
            {"_id": ObjectId(id)},
            {"$set": dados},
        )
        return resultado.matched_count > 0

    def buscar_por_horario(self, horario: datetime) -> list[Compromisso]:
        resultado = self.colecao.find({
            "data_horario": horario
        }).sort("data_horario", 1)

        return [
            Compromisso.from_dict(documento)
            for documento in resultado
        ]