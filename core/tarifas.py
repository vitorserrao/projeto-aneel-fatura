"""Representação e seleção de tarifas ACR.

Implementa apenas manipulação determinística de dados (filtros e vigência).
Nenhuma regra regulatória de resolução/precedência é assumida: quando mais de
uma tarifa atende aos critérios, o core se recusa a escolher silenciosamente
(docs/premissas.md, P6).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from .models import (
    COMPONENTES_SUPORTADOS,
    GRANDEZAS_SUPORTADAS,
    POSTOS_SUPORTADOS,
)


class TarifaNaoEncontrada(LookupError):
    """Nenhuma tarifa atende aos critérios informados."""


class AmbiguidadeTarifaria(LookupError):
    """Mais de uma tarifa atende aos critérios — sem regra de precedência validada."""


@dataclass(frozen=True)
class TarifaAcr:
    """Linha do dataset de Tarifas de Aplicação da ANEEL.

    Todos os campos exigidos pela especificação são preservados, sem
    eliminação silenciosa de informação (docs/dataset.md). Campos ainda não
    observados no dataset real podem permanecer vazios (pendência P5).
    """

    distribuidora: str
    resolucao: str
    inicio_vigencia: date | None = None
    fim_vigencia: date | None = None
    base_tarifaria: str = ""
    subgrupo: str = ""
    modalidade: str = ""
    classe: str = ""
    subclasse: str = ""
    detalhe: str = ""
    tipo_acesso: str = ""
    posto: str = ""
    unidade: str = ""
    tusd: float = 0.0
    te: float = 0.0

    def __post_init__(self) -> None:
        if not self.distribuidora.strip():
            raise ValueError("distribuidora não pode ser vazia")
        if not self.resolucao.strip():
            raise ValueError("resolucao não pode ser vazia")
        if (
            self.inicio_vigencia is not None
            and self.fim_vigencia is not None
            and self.inicio_vigencia > self.fim_vigencia
        ):
            raise ValueError("inicio_vigencia não pode ser posterior a fim_vigencia")
        if self.tusd < 0:
            raise ValueError("tusd não pode ser negativo")
        if self.te < 0:
            raise ValueError("te não pode ser negativo")


@dataclass(frozen=True)
class ParcelaTarifaria:
    """Parcela tarifária normalizada — entrada do motor de cálculo.

    Contrato do core: ``componente`` ∈ {TE, TUSD}, ``grandeza`` ∈ {ENERGIA,
    DEMANDA}, ``posto`` ∈ {PONTA, FORA PONTA} e ``unidade`` compatível com a
    grandeza (validada no motor). A normalização a partir do dataset ANEEL é
    responsabilidade da ingestão (Sprint 2; docs/premissas.md P1/P5).
    """

    componente: str
    grandeza: str
    posto: str
    unidade: str
    valor: float

    def __post_init__(self) -> None:
        # Normalização do contrato (não altera o significado tarifário).
        object.__setattr__(self, "componente", self.componente.strip().upper())
        object.__setattr__(self, "grandeza", self.grandeza.strip().upper())
        object.__setattr__(self, "posto", self.posto.strip().upper())
        object.__setattr__(self, "unidade", self.unidade.strip())

        if self.componente not in COMPONENTES_SUPORTADOS:
            raise ValueError(
                f"componente não suportado: {self.componente!r}; "
                f"use um de {COMPONENTES_SUPORTADOS}"
            )
        if self.grandeza not in GRANDEZAS_SUPORTADAS:
            raise ValueError(
                f"grandeza não suportada: {self.grandeza!r}; "
                f"use uma de {GRANDEZAS_SUPORTADAS}"
            )
        if self.posto not in POSTOS_SUPORTADOS:
            raise ValueError(
                f"posto não suportado: {self.posto!r}; use um de {POSTOS_SUPORTADOS}"
            )
        if not self.unidade:
            raise ValueError("unidade não pode ser vazia")
        if self.valor < 0:
            raise ValueError(f"valor não pode ser negativo (recebido {self.valor!r})")


def _normalizar_texto(valor: str) -> str:
    """Comparação case-insensitive e sem espaços nas bordas (não regulatória)."""
    return valor.strip().casefold()


def filtrar_tarifas(
    tarifas: Iterable[TarifaAcr],
    *,
    distribuidora: str | None = None,
    subgrupo: str | None = None,
    modalidade: str | None = None,
    classe: str | None = None,
    subclasse: str | None = None,
    posto: str | None = None,
) -> list[TarifaAcr]:
    """Filtra tarifas por igualdade de texto (case-insensitive, sem bordas).

    Filtros com valor ``None`` são ignorados. Determinístico: preserva a ordem
    de entrada das tarifas que atendem aos critérios.
    """
    criterios = {
        "distribuidora": _normalizar_texto(distribuidora) if distribuidora is not None else None,
        "subgrupo": _normalizar_texto(subgrupo) if subgrupo is not None else None,
        "modalidade": _normalizar_texto(modalidade) if modalidade is not None else None,
        "classe": _normalizar_texto(classe) if classe is not None else None,
        "subclasse": _normalizar_texto(subclasse) if subclasse is not None else None,
        "posto": _normalizar_texto(posto) if posto is not None else None,
    }
    selecionadas: list[TarifaAcr] = []
    for tarifa in tarifas:
        atende = all(
            criterio is None
            or _normalizar_texto(getattr(tarifa, campo)) == criterio
            for campo, criterio in criterios.items()
        )
        if atende:
            selecionadas.append(tarifa)
    return selecionadas


def tarifas_vigentes(
    tarifas: Iterable[TarifaAcr], data_referencia: date
) -> list[TarifaAcr]:
    """Tarifas cujo intervalo de vigência contém ``data_referencia`` (inclusive).

    Premissa estrutural A3 (docs/premissas.md): ``inicio_vigencia=None``
    significa sem limite inferior e ``fim_vigencia=None`` sem limite superior.
    Sobreposições não são resolvidas aqui — ver ``selecionar_unica``.
    """
    vigentes: list[TarifaAcr] = []
    for tarifa in tarifas:
        if tarifa.inicio_vigencia is not None and tarifa.inicio_vigencia > data_referencia:
            continue
        if tarifa.fim_vigencia is not None and tarifa.fim_vigencia < data_referencia:
            continue
        vigentes.append(tarifa)
    return vigentes


def selecionar_unica(
    tarifas: Iterable[TarifaAcr], *, contexto: str = "seleção de tarifa"
) -> TarifaAcr:
    """Retorna a única tarifa; recusa zero ou múltiplas (sem precedência assumida).

    Raises:
        TarifaNaoEncontrada: nenhuma tarifa atende aos critérios.
        AmbiguidadeTarifaria: mais de uma tarifa atende aos critérios.
    """
    candidatas = list(tarifas)
    if not candidatas:
        raise TarifaNaoEncontrada(f"Nenhuma tarifa atende aos critérios ({contexto}).")
    if len(candidatas) > 1:
        raise AmbiguidadeTarifaria(
            f"{len(candidatas)} tarifas atendem aos critérios ({contexto}); "
            "recusando-se a escolher sem regra de precedência validada "
            "(docs/premissas.md, P6)."
        )
    return candidatas[0]


def buscar_tarifa(
    tarifas: Iterable[TarifaAcr],
    data_referencia: date,
    *,
    distribuidora: str | None = None,
    subgrupo: str | None = None,
    modalidade: str | None = None,
    classe: str | None = None,
    subclasse: str | None = None,
    posto: str | None = None,
) -> TarifaAcr:
    """Aplica vigência + filtros e exige tarifa única (determinístico).

    Raises:
        TarifaNaoEncontrada: nenhuma tarifa atende aos critérios.
        AmbiguidadeTarifaria: mais de uma tarifa atende aos critérios.
    """
    vigentes = tarifas_vigentes(tarifas, data_referencia)
    candidatas = filtrar_tarifas(
        vigentes,
        distribuidora=distribuidora,
        subgrupo=subgrupo,
        modalidade=modalidade,
        classe=classe,
        subclasse=subclasse,
        posto=posto,
    )
    return selecionar_unica(candidatas, contexto="busca de tarifa")
