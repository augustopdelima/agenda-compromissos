from flask import Blueprint, flash, redirect, request, url_for

from helpers.formulario import (
    obter_dados_edicao,
    obter_dados_formulario,
    obter_url_retorno,
)
from helpers.renderizacao import (
    renderizar_detalhes,
    renderizar_edicao,
    renderizar_index,
    renderizar_pessoas,
)
from helpers.repositorios import (
    obter_compromisso_ou_404,
    obter_compromisso_repository,
    obter_pessoa_repository,
)
from models.compromisso import Compromisso
from validators.compromisso_validator import CompromissoValidador

compromisso_controller = Blueprint("compromisso", __name__)


@compromisso_controller.route("/", methods=["GET"], strict_slashes=False)
def index():
    return renderizar_index()


@compromisso_controller.route("/criar", methods=["POST"])
def criar():
    formulario = obter_dados_formulario()
    validator = CompromissoValidador(formulario, obter_pessoa_repository())

    if not validator.eh_valido():
        return renderizar_index(validator.erros, formulario, 400)

    obter_compromisso_repository().criar(Compromisso(**validator.dados_limpos))
    flash("Compromisso cadastrado com sucesso.", "success")
    return redirect(url_for("compromisso.index"))


@compromisso_controller.route("/<id>", methods=["GET"])
def detalhes(id):
    compromisso = obter_compromisso_ou_404(id)
    return renderizar_detalhes(compromisso)


@compromisso_controller.route("/<id>/editar", methods=["GET"])
def editar(id):
    compromisso = obter_compromisso_ou_404(id)
    return renderizar_edicao(compromisso, {})


@compromisso_controller.route("/<id>/editar", methods=["POST"])
def atualizar(id):
    compromisso = obter_compromisso_ou_404(id)
    formulario = obter_dados_edicao()
    validator = CompromissoValidador(formulario, modo="edicao")

    if not validator.eh_valido():
        return renderizar_edicao(compromisso, formulario, validator.erros, 400)

    obter_compromisso_repository().atualizar_titulo_descricao(
        id, validator.dados_limpos
    )
    flash("Compromisso atualizado com sucesso.", "success")
    return redirect(
        obter_url_retorno(url_for("compromisso.detalhes", id=id))
    )


@compromisso_controller.route("/<id>/excluir", methods=["POST"])
def excluir(id):
    obter_compromisso_ou_404(id)
    obter_compromisso_repository().excluir(id)
    flash("Compromisso excluído com sucesso.", "success")
    return redirect(url_for("compromisso.index"))


@compromisso_controller.route("/<id>/pessoas", methods=["GET"])
def gerenciar_pessoas(id):
    compromisso = obter_compromisso_ou_404(id)
    return renderizar_pessoas(compromisso, {})


@compromisso_controller.route("/<id>/pessoas", methods=["POST"])
def atualizar_pessoas(id):
    compromisso = obter_compromisso_ou_404(id)
    ids_pessoas = request.form.getlist("pessoas")
    validator = CompromissoValidador(
        {"pessoas": ids_pessoas}, obter_pessoa_repository(), modo="pessoas"
    )

    if not validator.eh_valido():
        return renderizar_pessoas(
            compromisso, {"pessoas": ids_pessoas}, validator.erros, 400
        )

    obter_compromisso_repository().atualizar_pessoas(
        id, validator.dados_limpos["pessoas"]
    )
    flash("Pessoas envolvidas atualizadas com sucesso.", "success")
    return redirect(
        obter_url_retorno(url_for("compromisso.detalhes", id=id))
    )
