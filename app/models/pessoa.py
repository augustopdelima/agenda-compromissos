class Pessoa:
    def __init__(self, nome: str, email: str, _id=None):
        self.id = str(_id) if _id else None
        self.nome = nome.strip()
        self.email = email.strip()

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "email" : self.email,
        }    
    
    @classmethod
    def from_dict(cls, dados: dict | None):
        if not dados:
            return None
        
        return cls(
            _id=dados.get("_id"),
            nome=dados.get("nome",""),
            email=dados.get("email","")
        )