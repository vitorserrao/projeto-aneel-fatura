"""Schemas de PI (Preço de Indiferença) — entrada/saída.

A entrada combina o perfil ACR (para buscar as TE da modalidade de menor
custo) com os parâmetros do cálculo do PI (tributos, perdas, encargos e
custos do ACL). Ver docs/epi.md e core/epi.py.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator


class EPISolicitacao(BaseModel):
    """Solicitação de cálculo do Preço de Indiferença (PI)."""

    distribuidora: str = Field(..., min_length=1, description="Sigla da distribuidora (ex.: CELESC)")
    subgrupo: str = Field(..., min_length=1, description="Subgrupo tarifário (ex.: A4)")
    data_referencia: str | None = Field(
        default=None,
        description="Data (AAAA-MM-DD) em que a tarifa deve estar vigente. None = hoje.",
    )
    modalidade: str | None = Field(
        default=None,
        description="Modalidade ACR a usar (ex.: Azul). None = modalidade de menor custo no ACR.",
    )
    atividade: str = Field(
        default="Comercial ou Industrial",
        description="Atividade econômica — só o Optante B usa: define o subgrupo B "
        "(B1 residencial, B2 rural, B3 demais) e a classe da tarifa (art. 292).",
    )

    consumo_ponta_kwh: float = Field(default=0.0, ge=0)
    consumo_fora_ponta_kwh: float = Field(default=0.0, ge=0)

    pis: float = Field(..., ge=0, lt=1, description="Alíquota de PIS (fração)")
    cofins: float = Field(..., ge=0, lt=1, description="Alíquota de COFINS (fração)")
    icms: float = Field(..., ge=0, lt=1, description="Alíquota de ICMS (fração)")

    k: float = Field(default=0.03, ge=0, description="Perdas na migração ao ACL (fração)")
    encargos: float = Field(
        default=0.0,
        ge=0,
        description="Encargos do ACL por energia (R$/MWh, ex.: ESS)",
    )
    opex_mensal: float = Field(default=0.0, ge=0, description="OPEX do ACL (R$/mês)")
    capex: float = Field(default=0.0, ge=0, description="CAPEX do ACL (R$)")
    horizonte_meses: int = Field(default=60, gt=0, description="Horizonte de amortização do CAPEX")

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

    @model_validator(mode="after")
    def _tributos_validos(self):
        if (1 - self.pis - self.cofins) <= 0:
            raise ValueError("PIS + COFINS deve ser menor que 1")
        return self


class EPIResultado(BaseModel):
    """Resultado do cálculo do PI."""

    pi: float
    modalidade: str
    bandeira_r_mwh: float
    e_mwh: float
    c_te: float
    c_e_acr: float
    custos_acl: float
    base_acl: float
    aviso: str | None = None
