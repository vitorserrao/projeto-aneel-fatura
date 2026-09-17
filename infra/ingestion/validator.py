"""Validação e geração de componentes tarifários para a carga.

A partir de um registro já normalizado (``cleaner.normalizar_registro``),
produz instâncias prontas para persistência. A divisão TE/TUSD segue a
decisão aprovada: cada coluna com valor aplicável gera um componente.

Nenhuma regra tarifária é criada aqui — apenas converte o que existe no CSV:
- componente ``TE``  quando ``vlr_te  != 0``;
- componente ``TUSD`` quando ``vlr_tusd != 0``.
Valores negativos e zeros são preservados (não descartados).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class RegistroValidado:
    """Registro já normalizado e pronto para persistência."""

    id_origem: int
    dat_geracao: date
    dat_inicio: date
    dat_fim: date
    dsc_reh: str | None
    dsc_base_tarifaria: str
    dsc_sub_grupo: str
    dsc_modalidade: str
    dsc_classe: str
    dsc_sub_classe: str
    dsc_detalhe: str
    nom_posto: str
    dsc_unidade: str
    sig_agente: str
    num_cnpj: str
    sig_acessante: str
    vlr_te: Decimal
    vlr_tusd: Decimal


def validar_registro(normalizado: dict[str, Any]) -> RegistroValidado:
    """Valida campos obrigatórios e vigência de um registro normalizado."""
    if normalizado["dat_inicio"] > normalizado["dat_fim"]:
        raise ValueError(
            f"linha {normalizado['id_origem']}: dat_inicio > dat_fim em vigência"
        )
    for campo in (
        "dsc_base_tarifaria",
        "dsc_sub_grupo",
        "dsc_modalidade",
        "dsc_classe",
        "dsc_detalhe",
        "nom_posto",
        "dsc_unidade",
        "sig_agente",
        "num_cnpj",
    ):
        if not normalizado[campo]:
            raise ValueError(f"linha {normalizado['id_origem']}: {campo} vazio")
    return RegistroValidado(**normalizado)


def _tem_valor(vlr: Decimal) -> bool:
    return vlr != 0


def componentes_do_registro(r: RegistroValidado) -> list[dict[str, object]]:
    """Gera as linhas-fato (componentes TE/TUSD) de um registro.

    Preserva ``linha_origem`` (= id_origem) e ``hash_linha`` para
    rastreabilidade 1:1 com a linha original do CSV.
    """
    comps: list[dict[str, object]] = []
    if _tem_valor(r.vlr_te):
        comps.append(
            {
                "componente": "TE",
                "valor": r.vlr_te,
                "linha_origem": r.id_origem,
            }
        )
    if _tem_valor(r.vlr_tusd):
        comps.append(
            {
                "componente": "TUSD",
                "valor": r.vlr_tusd,
                "linha_origem": r.id_origem,
            }
        )
    return comps
