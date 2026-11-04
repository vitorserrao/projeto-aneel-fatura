"""Contratos de entrada/saída do cálculo de fatura ACR.

A operação "perfil do consumidor → fatura" devolve as LINHAS da fatura
(estrutura do Simulador de Fatura) + totais + notas. Nenhuma fórmula aqui —
apenas a forma do resultado do core (``ResultadoFatura``/``LinhaFatura``).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LinhaFaturaOut(BaseModel):
    """Uma linha da fatura (tarifária ou adicional)."""

    descricao: str
    categoria: str
    quantidade: float
    tarifa: float
    custo: float


class FaturaOut(BaseModel):
    """Fatura de uma modalidade (linhas + total)."""

    modalidade: str
    base_tarifaria: str
    linhas: list[LinhaFaturaOut] = Field(default_factory=list)
    custo_tarifas: float = 0.0
    custo_total: float = 0.0
    aplicar_tributos: bool = False
    tarifas_nao_mapeadas: int = Field(
        default=0,
        description="Número de tarifas vigentes cujo posto/grandeza não foi "
        "mapeado (regra P5 pendente).",
    )
    pi: float | None = Field(
        default=None,
        description="Preço de Indiferença (R$/MWh) desta modalidade, quando "
        "calculado (docs/epi.md).",
    )


class Nota(BaseModel):
    """Nota de limitação/escopo do resultado (transparência)."""

    tipo: str
    mensagem: str


class FaturaResponse(BaseModel):
    """Resposta única da operação de cálculo de fatura."""

    fatura: FaturaOut
    notas: list[Nota] = Field(default_factory=list)


class ModalidadeIndisponivelOut(BaseModel):
    """Modalidade não disponível para o perfil e o motivo."""

    modalidade: str
    motivo: str


class ComparacaoOut(BaseModel):
    """Comparação Azul × Verde: ranking de disponíveis + indisponíveis."""

    disponiveis: list[FaturaOut] = Field(default_factory=list)
    indisponiveis: list[ModalidadeIndisponivelOut] = Field(default_factory=list)
    melhor: str | None = Field(
        default=None,
        description="Modalidade disponível de menor custo_total.",
    )


class ComparacaoResponse(BaseModel):
    """Resposta da operação de comparação de modalidades."""

    comparacao: ComparacaoOut
    notas: list[Nota] = Field(default_factory=list)
