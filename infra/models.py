"""Modelos SQLModel da infraestrutura (SQLModel como interface principal).

Estrutura aprovada (Sprint 2, decisão dec-2c889ec2080b7b85):

- ``distribuidora``  — dimensão da distribuidora, identidade por CNPJ.
- ``acessante``      — dimensão do acessante (SigAgenteAcessante).
- ``carga_aneel``    — proveniência/reprodutibilidade de cada ingestão.
- ``tarifa_aplicacao_componente`` — fato tarifário, 1 linha por componente
  (TE | TUSD) de cada linha do CSV real da ANEEL.

As definições de coluna/restrição preservam exatamente o DDL aprovado em
``scripts/ddl.sql``. Nenhuma regra de cálculo tarifário, precedência ou
interpretação regulatória reside aqui (pendências P5/P6).
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlmodel import Field, SQLModel


class Distribuidora(SQLModel, table=True):
    """Distribuidora de energia (identidade por CNPJ)."""

    __tablename__ = "distribuidora"
    __table_args__ = (
        CheckConstraint("num_cnpj <> ''", name="ck_distribuidora_cnpj_nao_vazio"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, autoincrement=True),
    )
    num_cnpj: str = Field(
        sa_column=Column(String(18), nullable=False, unique=True, index=True)
    )
    sig_agente: str = Field(sa_column=Column(String(60), nullable=False))
    criada_em: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )


class Acessante(SQLModel, table=True):
    """Acessante da tarifa (valor de ``SigAgenteAcessante``)."""

    __tablename__ = "acessante"
    __table_args__ = (
        CheckConstraint("sig_acessante <> ''", name="ck_acessante_sig_nao_vazio"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, autoincrement=True),
    )
    sig_acessante: str = Field(
        sa_column=Column(String(120), nullable=False, unique=True, index=True)
    )


class CargaAneel(SQLModel, table=True):
    """Proveniência de uma ingestão do dataset ANEEL."""

    __tablename__ = "carga_aneel"
    __table_args__ = (
        CheckConstraint("arquivo_origem <> ''", name="ck_carga_arquivo_nao_vazio"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    arquivo_origem: str = Field(sa_column=Column(Text, nullable=False))
    sha256_arquivo: str = Field(
        sa_column=Column(String(64), nullable=False, unique=True, index=True)
    )
    dat_geracao_conjunto: Optional[date] = Field(
        default=None, sa_column=Column(Date, nullable=True)
    )
    data_carga: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
    num_registros: Optional[int] = Field(
        default=None, sa_column=Column(Integer, nullable=True)
    )
    observacoes: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )


class BandeiraTarifaria(SQLModel, table=True):
    """Bandeira tarifária por competência mensal (fonte ANEEL/planilha)."""

    __tablename__ = "bandeira_tarifaria"
    __table_args__ = (
        UniqueConstraint("competencia", name="uq_bandeira_competencia"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    competencia: date = Field(sa_column=Column(Date, nullable=False))
    bandeira: str = Field(sa_column=Column(String(40), nullable=False))
    valor_mwh: Decimal = Field(sa_column=Column(Numeric(14, 6), nullable=False))
    valor_kwh: Decimal = Field(sa_column=Column(Numeric(14, 6), nullable=False))
    vigencia_inicio: Optional[date] = Field(default=None, sa_column=Column(Date))
    vigencia_fim: Optional[date] = Field(default=None, sa_column=Column(Date))
    fonte: Optional[str] = Field(default=None, sa_column=Column(Text))

    criado_em: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )


class TarifaAplicacaoComponente(SQLModel, table=True):
    """Fato tarifário: 1 linha por componente (TE ou TUSD).

    Uma linha do CSV real gera até duas linhas desta tabela (uma para TE e
    outra para TUSD) quando o valor correspondente é diferente de zero. O CSV
    original permanece intacto em ``data/raw/``; ``linha_origem`` preserva o
    ``_id`` do arquivo para rastreabilidade 1:1.
    """

    __tablename__ = "tarifa_aplicacao_componente"
    __table_args__ = (
        UniqueConstraint(
            "carga_id", "linha_origem", "componente",
            name="uq_tarifa_carga_linha_componente",
        ),
        CheckConstraint(
            "componente IN ('TE', 'TUSD')", name="ck_tarifa_componente_valido"
        ),
        CheckConstraint("valor IS NOT NULL", name="ck_tarifa_valor_nao_nulo"),
        CheckConstraint(
            "dat_inicio_vigencia <= dat_fim_vigencia", name="ck_tarifa_vigencia_valida"
        ),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    carga_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("carga_aneel.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        )
    )
    distribuidora_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("distribuidora.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        )
    )
    acessante_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("acessante.id", ondelete="RESTRICT"),
            nullable=True,
            index=True,
        ),
    )

    # Campos tarifários do CSV (nomes reais observados).
    dsc_reh: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    dat_inicio_vigencia: date = Field(sa_column=Column(Date, nullable=False))
    dat_fim_vigencia: date = Field(sa_column=Column(Date, nullable=False))
    dsc_base_tarifaria: str = Field(sa_column=Column(String(40), nullable=False))
    dsc_sub_grupo: str = Field(sa_column=Column(String(20), nullable=False))
    dsc_modalidade_tarifaria: str = Field(sa_column=Column(String(60), nullable=False))
    dsc_classe: str = Field(sa_column=Column(String(60), nullable=False))
    dsc_sub_classe: str = Field(sa_column=Column(String(120), nullable=False))
    dsc_detalhe: str = Field(sa_column=Column(String(60), nullable=False))
    nom_posto_tarifario: str = Field(sa_column=Column(String(60), nullable=False))
    dsc_unidade_terciaria: str = Field(sa_column=Column(String(10), nullable=False))

    componente: str = Field(sa_column=Column(String(4), nullable=False))
    valor: Decimal = Field(sa_column=Column(Numeric(14, 6), nullable=False))

    # Rastreabilidade com o CSV original.
    linha_origem: int = Field(sa_column=Column(Integer, nullable=False))
    hash_linha: str = Field(sa_column=Column(String(64), nullable=False))

    criado_em: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )


class BandeiraValor(SQLModel, table=True):
    """Valores históricos das bandeiras tarifárias (R$/MWh e R$/kWh).

    Uma linha por (bandeira, vigência a partir de). Para saber o valor vigente
    em uma competência, busca-se a última vigência <= competência de cada
    bandeira.
    """

    __tablename__ = "bandeira_valor"
    __table_args__ = (
        UniqueConstraint("bandeira", "vigencia_inicio", name="uq_bandeira_valor"),
    )

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    bandeira: str = Field(sa_column=Column(String(40), nullable=False))
    vigencia_inicio: date = Field(sa_column=Column(Date, nullable=False))
    valor_mwh: Decimal = Field(sa_column=Column(Numeric(14, 6), nullable=False))
    valor_kwh: Decimal = Field(sa_column=Column(Numeric(14, 6), nullable=False))
    fonte: Optional[str] = Field(default=None, sa_column=Column(Text))

    criado_em: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
