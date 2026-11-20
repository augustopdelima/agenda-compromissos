from urllib.parse import urlparse

from flask import request

from validators.compromisso_validator import CompromissoValidador


def url_interna_segura(url: str | None, fallback: str) -> str:
    """Aceita apenas URLs do mesmo host e diferentes da página atual."""
    if not url or not url.startswith(request.host_url):
        return fallback
    if urlparse(url).path == request.path:
        return fallback
    return url


def obter_url_cancelar(fallback: str) -> str:
    """Volta para a página anterior, desde que seja uma URL interna e diferente da atual."""
    return url_interna_segura(request.referrer, fallback)


def obter_url_retorno(fallback: str) -> str:
    """Recupera a página anterior enviada pelo formulário ao salvar."""
    return url_interna_segura(request.form.get("url_retorno"), fallback)


def obter_dados_formulario() -> dict:
    return {
        "data_horario": request.form.get("data_horario", ""),
        "titulo": request.form.get("titulo", ""),
        "descricao": request.form.get("descricao", ""),
        "pessoas": request.form.getlist("pessoas"),
    }


def obter_dados_edicao(campos: tuple | None = None) -> dict:
    """Lê apenas os campos permitidos que foram efetivamente enviados."""
    campos = campos or CompromissoValidador.CAMPOS_EDICAO
    return {
        campo: request.form[campo]
        for campo in campos
        if campo in request.form
    }
