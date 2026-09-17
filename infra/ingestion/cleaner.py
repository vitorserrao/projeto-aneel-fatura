"""Normalização técnica do dataset ANEEL (datas, decimal brasileiro, CNPJ).

Não implementa regra regulatória: apenas conversões de formato documentadas
para armazenamento consistente. O conteúdo textual original dos campos é
preservado tal como no CSV.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any


class DadoInvalido(ValueError):
    """Valor de um campo não pôde ser normalizado para o formato esperado."""


def normalizar_data(valor: str, campo: str) -> date:
    """Converte ``YYYY-MM-DD`` para ``datetime.date``."""
    if not valor.strip():
        raise DadoInvalido(f"{campo}: data vazia")
    try:
        return date.fromisoformat(valor.strip())
    except ValueError as exc:
        raise DadoInvalido(f"{campo}: data inválida {valor!r}") from exc


def normalizar_decimal(valor: str, campo: str) -> Decimal:
    """Converte decimal brasileiro (vírgula) para ``Decimal`` preservado.

    ``'1,85'`` -> ``Decimal('1.85')``; ``',00'`` -> ``Decimal('0.00')``.
    Usa Decimal (não float) para não perder precisão financeira. Aceita
    negativos; ``DscUnidade`` vazio já foi validado em outra etapa.
    """
    s = valor.strip().replace(".", "").replace(",", ".")
    if not s:
        raise DadoInvalido(f"{campo}: valor vazio")
    if s.startswith("."):
        s = "0" + s
    try:
        return Decimal(s)
    except Exception as exc:
        raise DadoInvalido(f"{campo}: valor decimal inválido {valor!r}") from exc


def normalizar_cnpj(valor: str) -> str:
    """Remove a máscara do CNPJ, mantendo só dígitos (consistência).

    Sem alterar conteúdo significativo: apenas elimina caracteres não
    numéricos. Campo obrigatório e deve ter exatamente 14 dígitos.
    """
    so_digitos = "".join(ch for ch in valor.strip() if ch.isdigit())
    if len(so_digitos) != 14:
        raise DadoInvalido(
            f"NumCNPJDistribuidora inválido {valor!r} (14 dígitos esperados)"
        )
    return so_digitos


def normalizar_registro(raw: dict[str, str]) -> dict[str, Any]:
    """Normaliza um registro bruto para os valores tipados.

    Retorna dict com: id_origem (int), dat_geracao (date),
    dat_inicio (date), dat_fim (date), num_cnpj (str 14), de_valores (Decimal).
    Textos traduzidos: dsc_reh (str|None), e os demais campos textuais com
    espaços preservados.
    """
    val = raw.get
    dsc_reh = val("DscREH") or None
    return {
        "id_origem": int(val("_id")),
        "dat_geracao": normalizar_data(val("DatGeracaoConjuntoDados"), "DatGeracaoConjuntoDados"),
        "dsc_reh": dsc_reh,
        "num_cnpj": normalizar_cnpj(val("NumCNPJDistribuidora")),
        "sig_agente": val("SigAgente").strip(),
        "dat_inicio": normalizar_data(val("DatInicioVigencia"), "DatInicioVigencia"),
        "dat_fim": normalizar_data(val("DatFimVigencia"), "DatFimVigencia"),
        "dsc_base_tarifaria": val("DscBaseTarifaria").strip(),
        "dsc_sub_grupo": val("DscSubGrupo").strip(),
        "dsc_modalidade": val("DscModalidadeTarifaria").strip(),
        "dsc_classe": val("DscClasse").strip(),
        "dsc_sub_classe": val("DscSubClasse").strip(),
        "dsc_detalhe": val("DscDetalhe").strip(),
        "nom_posto": val("NomPostoTarifario").strip(),
        "dsc_unidade": val("DscUnidadeTerciaria").strip(),
        "sig_acessante": val("SigAgenteAcessante").strip(),
        "vlr_tusd": normalizar_decimal(val("VlrTUSD"), "VlrTUSD"),
        "vlr_te": normalizar_decimal(val("VlrTE"), "VlrTE"),
    }
