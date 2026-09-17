"""Schemas de EPI (entrada/saída).

ESQUELETO — campos mínimos.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EPISolicitacao(BaseModel):
    """Solicitação de cálculo do EPI.

    Args:
        preco_referencia_acl: preço de referência do ACL fornecido pelo usuário.
    """

    preco_referencia_acl: float = Field(..., gt=0)


class EPIResultado(BaseModel):
    """Resultado do cálculo do EPI."""

    epi: float
