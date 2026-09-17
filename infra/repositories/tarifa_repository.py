"""Repositório de consultas de tarifas (Sprint 4).

Interface: SQLModel (modelos e ``select``); infraestrutura: SQLAlchemy
(engine/session). Somente leitura — não altera os dados da carga real.

Regra de vigência (intervalo inclusivo):

    dat_inicio_vigencia <= D AND dat_fim_vigencia >= D

Quando ``data`` é ``None``, a vigência não é filtrada (os demais filtros
continuam aplicados no PostgreSQL — nada é filtrado em Python após carregar).
Não há soma de TE/TUSD nesta camada: o motor de cálculo fica para as próximas
sprints. Sobrepõem-se múltiplos registros vigentes: todos são retornados.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlmodel import select
from sqlalchemy import text

from ..models import BandeiraTarifaria, Distribuidora, TarifaAplicacaoComponente


@dataclass(frozen=True)
class TarifaVigente:
    """Resultado estruturado de uma consulta de tarifa vigente."""

    num_cnpj: str
    sig_agente: str
    componente: str
    valor: Decimal
    resolucao: str
    inicio_vigencia: date
    fim_vigencia: date | None
    base_tarifaria: str
    subgrupo: str
    modalidade: str
    classe: str
    subclasse: str
    detalhe: str
    posto: str
    unidade: str


@dataclass(frozen=True)
class DistribuidoraInfo:
    """Identificação de distribuidora — identidade é o CNPJ."""

    num_cnpj: str
    sig_agente: str


class TarifaRepository:
    """Consultas sobre ``tarifa_aplicacao_componente`` + dimensões."""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    # ------------------------------------------------------------------ #
    # Consulta principal
    # ------------------------------------------------------------------ #
    def buscar_tarifas(
        self,
        *,
        data: date | None = None,
        num_cnpj: str | None = None,
        sig_agente: str | None = None,
        subgrupo: str | None = None,
        modalidade: str | None = None,
        classe: str | None = None,
        subclasse: str | None = None,
        detalhe: str | None = None,
        posto: str | None = None,
        unidade: str | None = None,
        componente: str | None = None,
        base_tarifaria: str | None = None,
    ) -> list[TarifaVigente]:
        """Busca tarifas vigentes (ou não, se ``data=None``) pelos filtros.

        Todos os filtros são opcionais e executados no PostgreSQL (WHERE/JOIN/
        ORDER BY). Resultado ordenado por início de vigência e componente.
        """
        stmt = (
            select(
                TarifaAplicacaoComponente,
                Distribuidora.num_cnpj,
                Distribuidora.sig_agente,
            )
            .join(
                Distribuidora,
                Distribuidora.id == TarifaAplicacaoComponente.distribuidora_id,
            )
        )

        if data is not None:
            stmt = stmt.where(
                TarifaAplicacaoComponente.dat_inicio_vigencia <= data,
                TarifaAplicacaoComponente.dat_fim_vigencia >= data,
            )
        if num_cnpj is not None:
            stmt = stmt.where(Distribuidora.num_cnpj == num_cnpj.strip())
        if sig_agente is not None:
            stmt = stmt.where(Distribuidora.sig_agente == sig_agente.strip())
        if subgrupo is not None:
            stmt = stmt.where(
                TarifaAplicacaoComponente.dsc_sub_grupo == subgrupo.strip()
            )
        if modalidade is not None:
            stmt = stmt.where(
                TarifaAplicacaoComponente.dsc_modalidade_tarifaria
                == modalidade.strip()
            )
        if classe is not None:
            stmt = stmt.where(TarifaAplicacaoComponente.dsc_classe == classe.strip())
        if subclasse is not None:
            stmt = stmt.where(
                TarifaAplicacaoComponente.dsc_sub_classe == subclasse.strip()
            )
        if detalhe is not None:
            stmt = stmt.where(
                TarifaAplicacaoComponente.dsc_detalhe == detalhe.strip()
            )
        if posto is not None:
            stmt = stmt.where(
                TarifaAplicacaoComponente.nom_posto_tarifario == posto.strip()
            )
        if unidade is not None:
            stmt = stmt.where(
                TarifaAplicacaoComponente.dsc_unidade_terciaria == unidade.strip()
            )
        if componente is not None:
            stmt = stmt.where(
                TarifaAplicacaoComponente.componente == componente.strip().upper()
            )
        if base_tarifaria is not None:
            stmt = stmt.where(
                TarifaAplicacaoComponente.dsc_base_tarifaria
                == base_tarifaria.strip()
            )

        stmt = stmt.order_by(
            TarifaAplicacaoComponente.dat_inicio_vigencia,
            TarifaAplicacaoComponente.componente,
        )

        with self._session_factory() as session:
            linhas = session.execute(stmt).all()

        return [
            TarifaVigente(
                num_cnpj=cnpj,
                sig_agente=sig,
                componente=t.componente,
                valor=t.valor,
                resolucao=t.dsc_reh or "",
                inicio_vigencia=t.dat_inicio_vigencia,
                fim_vigencia=t.dat_fim_vigencia,
                base_tarifaria=t.dsc_base_tarifaria,
                subgrupo=t.dsc_sub_grupo,
                modalidade=t.dsc_modalidade_tarifaria,
                classe=t.dsc_classe,
                subclasse=t.dsc_sub_classe,
                detalhe=t.dsc_detalhe,
                posto=t.nom_posto_tarifario,
                unidade=t.dsc_unidade_terciaria,
            )
            for (t, cnpj, sig) in linhas
        ]

    # ------------------------------------------------------------------ #
    # TE + TUSD (sem somar)
    # ------------------------------------------------------------------ #
    def buscar_componentes(
        self,
        *,
        data: date | None = None,
        num_cnpj: str | None = None,
        sig_agente: str | None = None,
        subgrupo: str | None = None,
        modalidade: str | None = None,
        classe: str | None = None,
        subclasse: str | None = None,
        detalhe: str | None = None,
        posto: str | None = None,
        unidade: str | None = None,
        base_tarifaria: str | None = None,
    ) -> dict[str, list[TarifaVigente]]:
        """Retorna TE e TUSD separados, sem soma: ``{"TE": [...], "TUSD": [...]}``."""
        tarifas = self.buscar_tarifas(
            data=data,
            num_cnpj=num_cnpj,
            sig_agente=sig_agente,
            subgrupo=subgrupo,
            modalidade=modalidade,
            classe=classe,
            subclasse=subclasse,
            detalhe=detalhe,
            posto=posto,
            unidade=unidade,
            base_tarifaria=base_tarifaria,
        )
        return {
            "TE": [t for t in tarifas if t.componente == "TE"],
            "TUSD": [t for t in tarifas if t.componente == "TUSD"],
        }

    # ------------------------------------------------------------------ #
    # Distribuidoras e filtros auxiliares
    # ------------------------------------------------------------------ #
    def buscar_bandeira(
        self, competencia: date
    ) -> tuple[str, float, float] | None:
        """Bandeira tarifária vigente na competência (mês/ano).

        Retorna ``(bandeira, valor_r_kwh, valor_r_mwh)`` ou ``None`` quando a
        competência é anterior ao início das bandeiras (jan/2015) — o motor
        trata esse caso como adicional 0 (mesma regra do ``IFERROR(...,0)``).
        """
        stmt = (
            select(BandeiraTarifaria)
            .where(BandeiraTarifaria.competencia == competencia.replace(day=1))
        )
        with self._session_factory() as session:
            linha = session.execute(stmt).scalars().first()
        if linha is None:
            return None
        return (
            linha.bandeira,
            float(linha.valor_kwh),
            float(linha.valor_mwh),
        )

    def buscar_bandeiras(self, competencia: date) -> dict[str, float]:
        """Valores vigentes (R$/kWh) de cada bandeira na competência.

        Para cada bandeira, usa a última vigência <= competência. Verde vale 0.
        """
        stmt = text("""
            SELECT DISTINCT ON (bandeira) bandeira, valor_kwh
            FROM bandeira_valor
            WHERE vigencia_inicio <= :c
            ORDER BY bandeira, vigencia_inicio DESC
        """)
        with self._session_factory() as session:
            linhas = session.execute(stmt, {"c": competencia}).all()
        valores = {"Verde": 0.0, "Amarela": 0.0, "Vermelha P1": 0.0, "Vermelha P2": 0.0}
        for bandeira, valor in linhas:
            valores[bandeira] = float(valor)
        return valores

    def listar_distribuidoras(self) -> list[DistribuidoraInfo]:
        """Distribuidoras cadastradas (identidade = CNPJ; sig é atributo)."""
        stmt = (
            select(Distribuidora.num_cnpj, Distribuidora.sig_agente)
            .order_by(Distribuidora.sig_agente, Distribuidora.num_cnpj)
        )
        with self._session_factory() as session:
            linhas = session.execute(stmt).all()
        return [
            DistribuidoraInfo(num_cnpj=cnpj, sig_agente=sig)
            for cnpj, sig in linhas
        ]

    def _valores_distintos(self, coluna) -> list[str]:
        stmt = select(coluna).distinct().order_by(coluna)
        with self._session_factory() as session:
            return list(session.execute(stmt).scalars().all())

    def listar_subgrupos(self) -> list[str]:
        return self._valores_distintos(TarifaAplicacaoComponente.dsc_sub_grupo)

    def listar_modalidades(self) -> list[str]:
        return self._valores_distintos(
            TarifaAplicacaoComponente.dsc_modalidade_tarifaria
        )

    def listar_classes(self) -> list[str]:
        return self._valores_distintos(TarifaAplicacaoComponente.dsc_classe)

    def listar_componentes(self) -> list[str]:
        return self._valores_distintos(TarifaAplicacaoComponente.componente)

    def listar_bases_tarifarias(self) -> list[str]:
        return self._valores_distintos(TarifaAplicacaoComponente.dsc_base_tarifaria)
