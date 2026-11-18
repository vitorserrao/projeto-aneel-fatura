"""Contratos de entrada/saída da comparação Verde × Azul."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator


class MesComparacao(BaseModel):
    """Um mês de fatura Verde usado para simular a Azul.

    ``None`` = dado ausente — nunca é interpretado como zero.
    """

    data_referencia: str = Field(..., description="Data (AAAA-MM-DD) da tarifa vigente do mês")
    data_leitura_anterior: str | None = Field(default=None, description="Leitura anterior (AAAA-MM-DD)")
    data_leitura_atual: str | None = Field(default=None, description="Leitura atual (AAAA-MM-DD)")

    dp: float | None = Field(default=None, ge=0, description="Demanda medida na ponta (kW)")
    dfp: float | None = Field(default=None, ge=0, description="Demanda medida fora de ponta (kW)")
    d_verde: float | None = Field(default=None, ge=0, description="Demanda única da fatura Verde (kW)")

    ep_kwh: float | None = Field(default=None, ge=0, description="Energia na ponta (kWh)")
    efp_kwh: float | None = Field(default=None, ge=0, description="Energia fora de ponta (kWh)")

    reativo_energia_ponta_kvArh: float | None = Field(default=None, ge=0)
    reativo_energia_fora_ponta_kvArh: float | None = Field(default=None, ge=0)
    reativo_energia_capacitiva_kvArh: float | None = Field(default=None, ge=0)
    reativo_demanda_ponta_kvAr: float | None = Field(default=None, ge=0)
    reativo_demanda_fora_ponta_kvAr: float | None = Field(default=None, ge=0)

    @field_validator("data_referencia", "data_leitura_anterior", "data_leitura_atual")
    @classmethod
    def _data_iso(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            date.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(f"data inválida (use AAAA-MM-DD): {v!r}") from exc
        return v


class ComparacaoVerdeAzulSolicitacao(BaseModel):
    """Solicitação de comparação Verde × Azul a partir de faturas Verde."""

    distribuidora: str = Field(..., min_length=1)
    subgrupo: str = Field(..., min_length=1)
    classe: str = Field(default="Não se aplica", min_length=1)
    detalhe: str = Field(default="Não se aplica")
    data_referencia: str | None = Field(default=None, description="Fallback de data do perfil")

    pis: float = Field(..., ge=0, lt=1)
    cofins: float = Field(..., ge=0, lt=1)
    icms: float = Field(..., ge=0, lt=1)
    tipo_icms: str = Field(default="fora", description="'dentro' (aditiva) ou 'fora' (multiplicativa)")

    contratada_atual: float | None = Field(default=None, ge=0, description="Demanda contratada atual da Verde (kW)")

    meses: list[MesComparacao] = Field(..., min_length=1)

    @field_validator("data_referencia")
    @classmethod
    def _data_iso(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            date.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(f"data_referencia inválida (use AAAA-MM-DD): {v!r}") from exc
        return v


class DcOtimasOut(BaseModel):
    """Demandas contratadas otimizadas (p, fp, verde)."""

    p: float | dict[str, float] | None = None
    fp: float | None = None
    verde: float | None = None


class ComparacaoVerdeAzulOut(BaseModel):
    """Resposta da comparação Verde × Azul."""

    nivel: int
    veredito: str
    verde_atual: float
    verde_otimizada: float
    azul: float | dict[str, float]
    dc_otimas: DcOtimasOut
    dp_equilibrio: float | None = None
    meses_analisados: int
    avisos: list[str] = Field(default_factory=list)
