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
- [x] Visualizar detalhes do compromisso (título, descrição, data/horário e pessoas)
- [x] Clicar em qualquer área do card para abrir os detalhes
- [x] Filtrar a listagem por **Todos**, **Futuros** e **Antigos** (padrão: Todos)
- [x] Alterar título e descrição de um compromisso
- [x] Alterar as pessoas envolvidas em um compromisso
- [x] Excluir uma pessoa de um compromisso
- [x] Excluir um compromisso com confirmação
- [x] Mensagens de sucesso ao salvar e excluir

### Interface
- [x] Layout responsivo: menu lateral no desktop e horizontal no mobile
- [x] Formulários de cadastro recolhidos em `<details>` (abrem sozinhos quando há erro ou via `#hash`)
- [x] Cards com descrição resumida ("ver mais") e no máximo 3 pessoas exibidas (`+N`)
- [x] Modal de confirmação para exclusão, acessível por teclado
- [x] Estados vazios centralizados, com atalho para cadastro
- [x] Cancelar ou salvar em formulários de edição retorna à página de origem
- [x] Skip link, foco visível e `aria-current` na navegação

## Estrutura do projeto

```
app/
├── app.py                          # Inicialização, SECRET_KEY e blueprints
├── controllers/                    # Rotas da aplicação
│   ├── home_controller.py
│   ├── pessoa_controller.py
│   └── compromisso_controller.py
├── helpers/                        # Funções auxiliares compartilhadas
│   ├── __init__.py
│   ├── periodo.py                  # Períodos e filtragem da listagem
│   ├── repositorios.py             # Repositórios em g e busca por id
│   ├── compromissos.py             # Agrupa compromissos com suas pessoas
│   ├── formulario.py               # Leitura do form e URLs de retorno
│   └── renderizacao.py             # Renderização dos templates de compromissos
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
│   ├── style.css                   # Arquivo legado, não carregado
│   └── css/                        # CSS dividido por responsabilidade
│       ├── tokens.css              # Cores, espaçamentos, raios e sombras
│       ├── base.css                # Reset, layout, menu e alertas
│       ├── formularios.css         # Campos, botões e mensagens de erro
│       ├── componentes.css         # Filtros, cards, modal e estados vazios
│       └── responsivo.css          # Breakpoints (carregado por último)
└── templates/                      # Templates Jinja2
    ├── base.html
    ├── index.html
    ├── 404.html
    ├── componentes/
    │   ├── aside.html
    │   ├── confirmar_acao.html
    │   ├── filtros_periodo.html
    │   ├── lista_compromissos.html
    │   └── lista_pessoas.html
    ├── compromissos/
    │   ├── index.html
    │   ├── detalhes.html
    │   ├── editar.html
    │   └── pessoas.html
    └── pessoas/
        └── index.html
tests/                              # Testes unitários e de rotas (unittest)
├── base.py                         # Banco em memória e app de teste
├── test_app_config.py
├── test_assets.py
├── test_helpers.py
├── test_models.py
├── test_routes.py
└── test_validators.py
```

**Camadas:** controller → helpers → validator → repository → model. Os controllers ficam apenas com as rotas; os helpers concentram filtros, acesso a repositórios, leitura de formulários e renderização. A validação fica isolada no validator e o acesso ao banco nos repositories.

**Referências de pessoas:** o documento do compromisso guarda apenas os ids das pessoas envolvidas, como strings. Não há exclusão em cascata: excluir uma pessoa do cadastro não altera compromissos, e ids que não correspondem mais a nenhuma pessoa cadastrada são ignorados na exibição e deixam de existir quando a lista é salva. Tanto o cadastro quanto a edição permitem lista vazia; basta não selecionar ninguém. A edição substitui a lista inteira.

## Variáveis de ambiente

Copie o `.env.example` para `.env` e ajuste os valores:

| Variável               | Descrição                                    |
| ---------------------- | -------------------------------------------- |
| `MONGO_ROOT_USERNAME`  | Usuário root do MongoDB                      |
| `MONGO_ROOT_PASSWORD`  | Senha do usuário root do MongoDB             |
| `MONGO_DATABASE`       | Nome do banco de dados                       |
| `SECRET_KEY`           | Chave usada pelo Flask para as mensagens `flash()` |

O app consome internamente `MONGO_URI` (montada pelo Compose a partir do usuário/senha) e `MONGO_DATABASE`. Se `SECRET_KEY` não estiver definida, o app usa uma chave apenas para desenvolvimento — defina um valor próprio em produção.

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

3. Acesse a visão geral em <http://localhost:5000/>.

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

4. Acesse a visão geral em <http://localhost:5000/>.

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

Nos exemplos sem Docker, defina também `SECRET_KEY` (`export SECRET_KEY="sua-chave"` no Linux/macOS ou `$env:SECRET_KEY = "sua-chave"` no PowerShell) para substituir a chave de desenvolvimento padrão.

## Testes

A suíte usa apenas `unittest` (já incluído no Python) e um banco em memória que simula as operações do PyMongo usadas pela aplicação. Não é preciso subir o MongoDB nem instalar pacotes extras.

Rodando na imagem do projeto (recomendado — já contém Flask e PyMongo):

```bash
docker run --rm -v "$PWD":/workspace -w /workspace \
  --entrypoint python agenda-compromissos-app:latest \
  -m unittest discover -s tests -v
```

Se a imagem ainda não existir, construa-a antes com `docker build -t agenda-compromissos-app .`.

Com as dependências instaladas localmente (`pip install -r requirements.txt`):

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem modelos, validadores, helpers, rotas e templates (filtros, detalhes, mensagens flash, retorno à página de origem e estados vazios), configuração da aplicação e estrutura do CSS.

## Endpoints

| Método | Rota | Descrição |
| ------ | ---- | --------- |
| GET | `/` | Visão geral com resumo e listagem filtrável de compromissos |
| GET | `/pessoas` | Listagem + formulário de cadastro de pessoas |
| POST | `/pessoas/criar` | Cadastra uma nova pessoa |
| GET | `/compromissos` | Listagem + formulário de cadastro de compromissos |
| POST | `/compromissos/criar` | Cadastra um novo compromisso |
| GET | `/compromissos/<id>` | Detalhes do compromisso (título, descrição, horário e pessoas) |
| GET | `/compromissos/<id>/editar` | Formulário de título e descrição |
| POST | `/compromissos/<id>/editar` | Salva título e descrição |
| GET | `/compromissos/<id>/pessoas` | Gerencia as pessoas envolvidas |
| POST | `/compromissos/<id>/pessoas` | Substitui a lista de envolvidas |
| POST | `/compromissos/<id>/excluir` | Exclui um compromisso |

As listagens de compromissos aceitam `?periodo=todos|proximos|passados`. O padrão é `todos`, e os rótulos exibidos são **Todos**, **Futuros** e **Antigos**, respectivamente.

## Roadmap

As próximas funcionalidades estão mapeadas nas [issues do repositório](../../issues).
