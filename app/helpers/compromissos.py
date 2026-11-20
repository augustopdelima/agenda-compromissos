from helpers.repositorios import obter_pessoa_repository


def montar_compromissos_com_pessoas(compromissos: list) -> list[dict]:
    ids_pessoas = [
        id_pessoa
        for compromisso in compromissos
        for id_pessoa in compromisso.pessoas
    ]

    pessoas = obter_pessoa_repository().buscar_por_ids(ids_pessoas)
    pessoas_por_id = {pessoa.id: pessoa for pessoa in pessoas}

    return [
        {
            "compromisso": compromisso,
            "pessoas": [
                pessoas_por_id[id_pessoa]
                for id_pessoa in compromisso.pessoas
                if id_pessoa in pessoas_por_id
            ]
        }
        for compromisso in compromissos
    ]
