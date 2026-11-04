"""Schemas do planejamento anual de modalidades."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator


class MesPlanejamento(BaseModel):
    """Um mês do histórico (1 a 12 meses)."""

    data_referencia: str = Field(..., description="Data (AAAA-MM-DD) da vigência/tarifa do mês")
    d_med_ponta: float | None = Field(default=None, ge=0, description="Demanda medida ponta (kW)")
    d_med_fora_ponta: float | None = Field(default=None, ge=0, description="Demanda medida fora de ponta (kW)")
    d_med_unica: float | None = Field(default=None, ge=0, description="Demanda medida única (kW, fatura Verde)")
    e_ponta_kwh: float = Field(default=0.0, ge=0, description="Energia ponta (kWh)")
    e_fora_ponta_kwh: float = Field(default=0.0, ge=0, description="Energia fora de ponta (kWh)")

    @field_validator("data_referencia")
    @classmethod
    def _data_iso(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(f"data_referencia inválida (use AAAA-MM-DD): {v!r}") from exc
        return v


class PlanejamentoSolicitacao(BaseModel):
    """Solicitação do comparativo anual (contrato atual × demanda otimizada)."""

    distribuidora: str = Field(..., min_length=1)
    subgrupo: str = Field(..., min_length=1)
    classe: str = Field(default="Não se aplica", min_length=1)
    detalhe: str = Field(default="Não se aplica")
    atividade: str = Field(default="Comercial ou Industrial")
    tipo_ligacao: str = Field(default="Trifásico")
    data_referencia: str | None = Field(default=None, description="Fallback de data para o perfil")

    meses: list[MesPlanejamento] = Field(..., min_length=1, max_length=12)

    pis: float = Field(..., ge=0, lt=1)
    cofins: float = Field(..., ge=0, lt=1)
    icms: float = Field(..., ge=0, lt=1)
    tipo_icms: str = Field(default="fora", description="'dentro' (aditiva) ou 'fora' (multiplicativa)")

    modalidade_atual: str = Field(default="Verde", description="Azul ou Verde")
    dc_atual_verde: float | None = Field(default=None, ge=0)
    dc_atual_azul_ponta: float | None = Field(default=None, ge=0)
    dc_atual_azul_fora: float | None = Field(default=None, ge=0)

    k: float = Field(default=0.03, ge=0)
    encargos: float = Field(default=0.0, ge=0)
    opex_mensal: float = Field(default=0.0, ge=0)
    capex: float = Field(default=0.0, ge=0)
    horizonte_meses: int = Field(default=60, gt=0)

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
