"""Contratos de consulta (leitura) — usados pela API de dados.

Espelham os filtros que o ``TarifaRepository.buscar_tarifas`` aceita e o objeto
de retorno ``TarifaVigente`` (definido no repository). Sem fórmula: só o
contrato de entrada/saída da camada de leitura, para que a API de consulta e as
futuras rotas de cálculo sejam construídas sobre um tipo estável.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Componente = Literal["TE", "TUSD"]


class FiltroConsultaTarifa(BaseModel):
    """Filtros opcionais para buscar tarifas vigentes.

    Todos os campos são opcionais (None = não filtra). A vigência é restrita
    por ``data`` (intervalo inclusivo) quando informada.
    """

    num_cnpj: str | None = Field(default=None, description="CNPJ da distribuidora (identidade)")
    sig_agente: str | None = Field(default=None, description="Sigla da distribuidora (atributo)")
    data: str | None = Field(
        default=None, description="Data AAAA-MM-DD de referência (vigência)"
    )
    subgrupo: str | None = None
    modalidade: str | None = None
    classe: str | None = None
    subclasse: str | None = None
    detalhe: str | None = None
    posto: str | None = None
    unidade: str | None = None
    componente: Componente | None = None
    base_tarifaria: str | None = None


class TarifaConsultaOut(BaseModel):
    """Resultado de uma linha tarifária vigente, idêntico ao ``TarifaVigente``.

    Formato textual/normalizado para a API; valores numéricos como ``Decimal``
    para preservar precisão (sem converter para float).
    """

    num_cnpj: str
    sig_agente: str
    componente: Componente
    valor: float
    resolucao: str | None = None
    inicio_vigencia: str | None
    fim_vigencia: str | None
    base_tarifaria: str
    subgrupo: str
    modalidade: str
    classe: str
    subclasse: str
    detalhe: str
    posto: str
    unidade: str


class DistribuidoraOut(BaseModel):
    """Distribuidora retornada pela API (identidade = CNPJ)."""

    num_cnpj: str
    sig_agente: str
