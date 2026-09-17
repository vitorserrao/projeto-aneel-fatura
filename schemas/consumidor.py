"""Schema do perfil do consumidor (entrada).

Perfil real, alinhado ao domínio do core (``core.models.Consumidor``) e aos
campos que o TarifaRepository/consultas usam (distribuidora, subgrupo,
modalidade, posto, data). Não contém regra tarifária — é apenas o contrato de
entrada.

A modalidade é um parâmetro da simulação (não uma propriedade fixa do
consumidor): permite comparar o mesmo perfil sob modalidades diferentes.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

# Modalidades reconhecidas pelo MVP. Aplicabilidade ao subgrupo/perfil é
# validada na camada de serviço/regras (docs/premissas.md), não aqui.
MODALIDADES_MVP = ("AZUL", "VERDE")


class Consumidor(BaseModel):
    """Perfil físico/contratual do consumidor.

    Consumo/demanda separados por posto (ponta/fora de ponta): necessário para
    as modalidades Azul e Verde. Valores 0 em um posto significam "não
    informado" para aquele posto; a regra de qual posto é aplicável fica no
    futuro motor/regras.
    """

    distribuidora: str = Field(
        ..., min_length=1, description="Sigla/nome da distribuidora (ex.: CPFL JAGUARI)"
    )
    subgrupo: str = Field(
        ..., min_length=1, description="Subgrupo tarifário (ex.: A2, A4, B3)"
    )
    modalidade: str | None = Field(
        default=None,
        description=f"Modalidade a simular, se conhecida ({MODALIDADES_MVP}). "
        "None = ainda não definida (otimização decide).",
    )
    classe: str = Field(default="Nao se aplica", min_length=1)
    subclasse: str = Field(default="Nao se aplica")
    data_referencia: str | None = Field(
        default=None,
        description="Data (AAAA-MM-DD) em que a tarifa deve estar vigente. None = atual.",
    )

    detalhe: str = Field(
        default="Não se aplica",
        description="Detalhe tarifário do dataset (ex.: 'Não se aplica', APE, SCEE). "
        "Filtra a tarifa correta e evita somar linhas sobrepostas (P6).",
    )

    consumo_ponta_kwh: float = Field(default=0.0, ge=0)
    consumo_fora_ponta_kwh: float = Field(default=0.0, ge=0)
    demanda_ponta_kw: float = Field(default=0.0, ge=0)
    demanda_fora_ponta_kw: float = Field(default=0.0, ge=0)
    # Demanda contratada: a faturável é o MAIOR entre contratada e medida.
    demanda_contratada_ponta_kw: float = Field(default=0.0, ge=0)
    demanda_contratada_fora_ponta_kw: float = Field(default=0.0, ge=0)

    # Demanda ÚNICA (Verde): faturável = máx(medida, contratada). Sem
    # separação por posto (REN 1.000/2021).
    demanda_medida_unica_kw: float = Field(default=0.0, ge=0)
    demanda_contratada_unica_kw: float = Field(default=0.0, ge=0)

    # Rateio de consumo entre leituras (fração ∈ [0,1]).
    percentual_mes_anterior: float = Field(default=0.0, ge=0, le=1)

    # Linhas adicionais da fatura (Simulador de Fatura anterior).
    bandeira_adicional_r_kwh: float = Field(default=0.0, ge=0)
    cip_cosip_rs: float = Field(default=0.0, ge=0)
    outros_rs: float = Field(default=0.0, ge=0)
    reativo_energia_ponta_kvArh: float = Field(default=0.0, ge=0)
    reativo_energia_fora_ponta_kvArh: float = Field(default=0.0, ge=0)
    reativo_demanda_ponta_kvAr: float = Field(default=0.0, ge=0)
    reativo_demanda_fora_ponta_kvAr: float = Field(default=0.0, ge=0)

    @field_validator("data_referencia")
    @classmethod
    def _data_iso(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            from datetime import date
            date.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(f"data_referencia inválida (use AAAA-MM-DD): {v!r}") from exc
        return v

    @field_validator("modalidade")
    @classmethod
    def _modalidade_valida(cls, v: str | None) -> str | None:
        if v is None:
            return None
        m = v.strip().upper()
        if m not in MODALIDADES_MVP:
            raise ValueError(
                f"modalidade {v!r} não reconhecida; use uma de {MODALIDADES_MVP} ou None"
            )
        return m

    @property
    def consumo_total_kwh(self) -> float:
        return self.consumo_ponta_kwh + self.consumo_fora_ponta_kwh
