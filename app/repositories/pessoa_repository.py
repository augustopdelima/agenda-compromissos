from models.pessoa import Pessoa

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

    def buscar_por_email(self, email:str) -> Pessoa | None:
        doc = self.colecao.find_one({"email": email.strip().lower()})
        return Pessoa.from_dict(doc)