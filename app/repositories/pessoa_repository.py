from models.pessoa import Pessoa

from bson import ObjectId

class PessoaRepository:
    def __init__(self, db):
        self.colecao = db["pessoas"]

    def garantir_indices(self):
        self.colecao.create_index("email", unique=True)

    def criar(self, pessoa:Pessoa) -> Pessoa:
        resultado = self.colecao.insert_one(pessoa.to_dict())
        pessoa.id = str(resultado.inserted_id)
        return pessoa

    def buscar_todos(self) -> list[Pessoa]:
        cursor = self.colecao.find().sort("nome", 1)
        return [Pessoa.from_dict(doc) for doc in cursor]

    def buscar_por_id(self, id: str) -> Pessoa | None:
        if not ObjectId.is_valid(id):
            return None

        documento = self.colecao.find_one({"_id": ObjectId(id)})
        return Pessoa.from_dict(documento)

    def buscar_por_ids(self, ids: list) -> list[Pessoa]:
        if not ids:
            return []

        documentos = self.colecao.find({
            "_id": {"$in": [ObjectId(id_pessoa) for id_pessoa in ids]}
        })
        return [Pessoa.from_dict(doc) for doc in documentos]

    def buscar_por_email(self, email:str) -> Pessoa | None:
        doc = self.colecao.find_one({"email": email.strip().lower()})
        return Pessoa.from_dict(doc)

    def atualizar(self, id: str, dados: dict) -> bool:
        if not ObjectId.is_valid(id) or not dados:
            return False

        resultado = self.colecao.update_one(
            {"_id": ObjectId(id)},
            {"$set": dados},
        )
        return resultado.matched_count > 0