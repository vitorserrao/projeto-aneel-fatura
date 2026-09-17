"""Contratos de resposta do cálculo ACR e otimização (saída).

Ainda não há fórmula implementada (o motor/regras de mercado serão definidos
após estudo — docs/premissas.md). Este arquivo define apenas a FORMA dos
resultados que a API de cálculo devolverá, para que a camada de consulta /
interface sejam construídas sobre um contrato estável desde já.

Nenhum valor de resultado é calculado/preenchido aqui.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ParcelaCustoOut(BaseModel):
    """Descrição de uma parcela de custo (forma; sem valor de regra)."""

    componente: Literal["TE", "TUSD"]
    grandeza: Literal["ENERGIA", "DEMANDA"]
    posto: Literal["PONTA", "FORA PONTA"]
    quantidade: Optional[float] = None
    tarifa: Optional[float] = None
    custo: Optional[float] = None


class ResultadoCalculoOut(BaseModel):
    """Estrutura de retorno de um cálculo ACR (forma; preenchido futuramente)."""

    modalidade: str
    parcelas: list[ParcelaCustoOut] = Field(default_factory=list)
    custo_energia: Optional[float] = None
    custo_demanda: Optional[float] = None
    custo_total: Optional[float] = None
    # Componentes e notas serão adicionados quando a regra for fechada.


class ResultadoOtimizacaoOut(BaseModel):
    """Estrutura de retorno da otimização de modalidades (forma)."""

    modalidade_escolhida: Optional[str] = None
    custos_por_modalidade: dict[str, Optional[float]] = Field(default_factory=dict)
