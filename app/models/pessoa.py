class Pessoa:
    def __init__(self, nome: str, email: str, _id=None):
        self.id = str(_id) if _id else None
        self.nome = nome.strip()
        self.email = email.strip()

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "email": self.email
        }

    @classmethod
    def from_dict(cls, data: dict | None):
        if not data:
            return None
        return cls(
            _id=data.get("_id"),
            nome=data.get("nome",""),
            email=data.get("email","")
        )