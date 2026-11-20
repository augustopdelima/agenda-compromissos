# agenda-compromissos

Agenda de compromissos com data/horário, título, descrição e pessoas envolvidas. Cada pessoa é cadastrada separadamente na coleção `pessoas`; cada compromisso guarda apenas os ids das pessoas vinculadas.

## Stack

- **Python 3.15** + [Flask](https://flask.palletsprojects.com/)
- **MongoDB** via [PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/)
- **Docker / Docker Compose** para ambiente e execução

## Funcionalidades

### Pessoas
- [x] Cadastrar pessoa (nome + e-mail, com e-mail único)
- [x] Listar pessoas

### Agenda (compromissos)
- [x] Listar compromissos
- [x] Cadastrar novo compromisso
- [x] Alterar título e descrição de um compromisso
- [x] Alterar as pessoas envolvidas em um compromisso
- [x] Excluir uma pessoa de um compromisso
- [x] Excluir um compromisso

## Estrutura do projeto

```
app/
├── app.py                          # Inicialização e registro dos blueprints
├── controllers/                    # Rotas da aplicação
│   ├── home_controller.py
│   ├── pessoa_controller.py
│   └── compromisso_controller.py
├── models/                         # Entidades de domínio
│   ├── pessoa.py
│   └── compromisso.py
├── repositories/                   # Acesso ao MongoDB
│   ├── pessoa_repository.py
│   └── compromisso_repository.py
├── validators/                     # Validação dos dados de formulário
│   ├── pessoa_validator.py
│   └── compromisso_validator.py
├── static/
│   └── style.css
└── templates/                      # Templates Jinja2
    ├── base.html
    ├── index.html
    ├── 404.html
    ├── componentes/
    │   ├── aside.html
    │   ├── confirmar_acao.html
    │   ├── lista_compromissos.html
    │   └── lista_pessoas.html
    ├── compromissos/
    │   ├── index.html
    │   ├── editar.html
    │   └── pessoas.html
    └── pessoas/
        └── index.html
```

**Camadas:** controller → validator → repository → model. As rotas ficam nos controllers, a validação fica isolada no validator e o acesso ao banco fica nos repositories.

**Referências de pessoas:** o documento do compromisso guarda apenas os ids das pessoas envolvidas, como strings. Não há exclusão em cascata: excluir uma pessoa do cadastro não altera compromissos, e ids que não correspondem mais a nenhuma pessoa cadastrada são ignorados na exibição e deixam de existir quando a lista é salva. Tanto o cadastro quanto a edição permitem lista vazia; basta não selecionar ninguém. A edição substitui a lista inteira.

## Variáveis de ambiente

Copie o `.env.example` para `.env` e ajuste os valores:

| Variável               | Descrição                                    |
| ---------------------- | -------------------------------------------- |
| `MONGO_ROOT_USERNAME`  | Usuário root do MongoDB                      |
| `MONGO_ROOT_PASSWORD`  | Senha do usuário root do MongoDB             |
| `MONGO_DATABASE`       | Nome do banco de dados                       |

O app consome internamente `MONGO_URI` (montada pelo Compose a partir do usuário/senha) e `MONGO_DATABASE`.

## Como rodar

Pré-requisitos: [Docker](https://docs.docker.com/get-docker/) com o plugin Compose.

1. Configure as variáveis de ambiente:

   ```bash
   cp .env.example .env
   ```

2. Suba os containers (app + MongoDB):

   ```bash
   docker compose up --build
   ```

3. Acesse em <http://localhost:5000/pessoas>.

O código em `app/` é montado como volume no container, então alterações aparecem automaticamente (o Flask roda em modo debug). O MongoDB persiste os dados no volume `mongodb_data`.

### Rodando no Windows

1. Instale o [Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/) (com o WSL2 habilitado) e deixe-o em execução.

2. Abra o **PowerShell** ou o **Prompt de Comando** na pasta do projeto e configure as variáveis de ambiente:

   ```powershell
   copy .env.example .env
   ```

3. Suba os containers (app + MongoDB):

   ```powershell
   docker compose up --build
   ```

4. Acesse em <http://localhost:5000/pessoas>.

> **Sem Docker (opcional):** é necessário ter o [Python 3.15](https://www.python.org/downloads/windows/) instalado (marcando a opção "Add Python to PATH" no instalador) e um MongoDB rodando localmente na porta 27017.
>
> No **PowerShell**:
>
> ```powershell
> pip install -r requirements.txt
> $env:MONGO_URI = "mongodb://localhost:27017"
> $env:MONGO_DATABASE = "mongo_database"
> flask --app app:iniciar_app run --debug
> ```
>
> No **Prompt de Comando (cmd)**:
>
> ```cmd
> pip install -r requirements.txt
> set MONGO_URI=mongodb://localhost:27017
> set MONGO_DATABASE=mongo_database
> flask --app app:iniciar_app run --debug
> ```

### Rodando sem Docker no Linux/macOS (opcional)

```bash
pip install -r requirements.txt
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DATABASE="mongo_database"
flask --app app:iniciar_app run --debug
```

## Endpoints

| Método | Rota | Descrição |
| ------ | ---- | --------- |
| GET | `/` | Home com listagem de compromissos |
| GET | `/pessoas` | Listagem + formulário de cadastro de pessoas |
| POST | `/pessoas/criar` | Cadastra uma nova pessoa |
| GET | `/compromissos` | Listagem + formulário de cadastro de compromissos |
| POST | `/compromissos/criar` | Cadastra um novo compromisso |
| GET | `/compromissos/<id>/editar` | Formulário de título e descrição |
| POST | `/compromissos/<id>/editar` | Salva título e descrição |
| GET | `/compromissos/<id>/pessoas` | Gerencia as pessoas envolvidas |
| POST | `/compromissos/<id>/pessoas` | Substitui a lista de envolvidas |
| POST | `/compromissos/<id>/excluir` | Exclui um compromisso |

## Roadmap

As próximas funcionalidades estão mapeadas nas [issues do repositório](../../issues).
