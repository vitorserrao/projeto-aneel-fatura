"""Planejamento anual de modalidades tarifárias (core puro).

Implementa, sem depender de infraestrutura, os itens A–D do comparador anual:

A) Montagem da demanda medida por posto (com regra para dado ausente);
B) Otimização da demanda contratada por modalidade (menor custo anual);
C) Demanda de ponta de equilíbrio (Azul × Verde) quando a ponta é estimada;
D) Comparação em dois cenários (contrato atual × demanda otimizada) com
   decomposição do ganho.

O core NÃO busca tarifas nem calcula a fatura completa — ele recebe funções
de custo injetáveis (``custo_fn``). Quem conhece o motor (services) injeta o
custo mensal real (fatura completa com tributos); os testes injetam funções
sintéticas só de demanda. Assim o otimizador é testável isoladamente e
reutiliza o motor existente sem alterar suas regras.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Constantes e vocabulário
# ---------------------------------------------------------------------------

DC_MINIMO_GRUPO_A = 30.0  # mínimo regulatório do Grupo A (kW)
PASSO_PADRAO = 1.0  # passo da busca discreta (kW)
TOLERANCIA_ULTRAPASSAGEM = 0.05  # art. 301: 5%
FATOR_ULTRAPASSAGEM = 2.0  # art. 301: 2 × tarifa de ultrapassagem
TOLERANCIA_EQUILIBRIO_KW = 0.1

AVISO_DEMANDA_PONTA_ESTIMADA = (
    "Demanda de ponta não informada; adotada igual à demanda única "
    "(estimativa conservadora para a Azul)."
)
AVISO_DEMANDA_OTIMA_REFERENCIA = (
    "Demanda ótima calculada como referência: a adoção está sujeita às "
    "regras de alteração contratual da REN 1.000/2021 (não implementadas)."
)


def _aviso_meses_parciais(n: int) -> str:
    return (
        f"Foram informados {n} mês(es); o comparativo anual considera 12 "
        "meses. Resultados com menos de 12 meses são parciais."
    )

POSTO_PONTA = "PONTA"
POSTO_FORA_PONTA = "FORA PONTA"


# ---------------------------------------------------------------------------
# Estruturas de dados
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MedicaoMensal:
    """Medições de demanda de um mês (kW). Campos opcionais = não informado."""

    d_med_ponta: float | None = None
    d_med_fora_ponta: float | None = None
    d_med_unica: float | None = None


@dataclass(frozen=True)
class DemandaPorModalidade:
    """Demanda medida usada por modalidade em um mês."""

    azul_ponta: float
    azul_fora_ponta: float
    verde: float


@dataclass(frozen=True)
class CustoDemandaMensal:
    """Resultado mensal do faturamento de demanda (um posto)."""

    faturavel_kw: float
    ultrapassagem_kw: float
    ociosidade_kw: float
    custo: float


@dataclass(frozen=True)
class ResultadoContrato:
    """Otimização de UMA variável de demanda contratada (Verde ou um posto)."""

    dc: float
    custo_anual: float
    custos_mensais: tuple[float, ...]
    faturavel_mensal: tuple[float, ...]
    ultrapassagem_mensal: tuple[float, ...]  # kW
    ociosidade_mensal: tuple[float, ...]  # kW


@dataclass(frozen=True)
class ResultadoContratoAzul:
    """Otimização das duas demandas contratadas da Azul (postos independentes)."""

    ponta: ResultadoContrato
    fora_ponta: ResultadoContrato

    @property
    def custo_anual(self) -> float:
        return self.ponta.custo_anual + self.fora_ponta.custo_anual


@dataclass(frozen=True)
class ResultadoEquilibrio:
    """Demanda de ponta de equilíbrio Azul × Verde."""

    dp_eq: float | None
    mensagem: str
    azul_sempre_melhor: bool = False
    verde_sempre_melhor: bool = False


@dataclass(frozen=True)
class GanhoComparacao:
    """Decomposição do ganho anual."""

    ganho_total: float
    ganho_demanda: float
    ganho_modalidade: float


@dataclass(frozen=True)
class ResultadoModalidadePlanejamento:
    """Resultado anual de uma modalidade nos dois cenários."""

    modalidade: str
    custo_contrato_atual: float
    custo_demanda_otimizada: float
    dc_atual: float | tuple[float, float] | None
    dc_otima: float | tuple[float, float]
    detalhe: ResultadoContrato | ResultadoContratoAzul


@dataclass(frozen=True)
class ResultadoPlanejamento:
    """Comparação anual completa (item D)."""

    modalidades: tuple[ResultadoModalidadePlanejamento, ...]
    melhor_contrato_atual: str
    melhor_demanda_otimizada: str
    ganho: GanhoComparacao
    avisos: tuple[str, ...]
    equilibrio: ResultadoEquilibrio | None = None


# ---------------------------------------------------------------------------
# A) Montagem da demanda medida por posto
# ---------------------------------------------------------------------------


def montar_demanda(mes: MedicaoMensal) -> tuple[DemandaPorModalidade, str | None]:
    """Aplica a regra de dado ausente a um mês (item A)."""
    if mes.d_med_ponta is not None and mes.d_med_fora_ponta is not None:
        return (
            DemandaPorModalidade(
                azul_ponta=mes.d_med_ponta,
                azul_fora_ponta=mes.d_med_fora_ponta,
                verde=max(mes.d_med_ponta, mes.d_med_fora_ponta),
            ),
            None,
        )
    if mes.d_med_unica is not None:
        return (
            DemandaPorModalidade(
                azul_ponta=mes.d_med_unica,
                azul_fora_ponta=mes.d_med_unica,
                verde=mes.d_med_unica,
            ),
            AVISO_DEMANDA_PONTA_ESTIMADA,
        )
    raise ValueError(
        "mês sem demanda medida: informe d_med_ponta/d_med_fora_ponta ou d_med_unica"
    )


def montar_demandas(
    meses: Sequence[MedicaoMensal],
) -> tuple[list[DemandaPorModalidade], list[str]]:
    """Monta as demandas dos 12 meses e devolve ``(demandas, avisos)``."""
    demandas: list[DemandaPorModalidade] = []
    avisos: list[str] = []
    if len(meses) < 12:
        avisos.append(_aviso_meses_parciais(len(meses)))
    for mes in meses:
        demanda, aviso = montar_demanda(mes)
        demandas.append(demanda)
        if aviso and aviso not in avisos:
            avisos.append(aviso)
    return demandas, avisos


# ---------------------------------------------------------------------------
# B) Otimização da demanda contratada
# ---------------------------------------------------------------------------


def custo_demanda_mensal(
    d_med: float,
    dc: float,
    tarifa: float,
    fator_ultrapassagem: float = FATOR_ULTRAPASSAGEM,
    tolerancia: float = TOLERANCIA_ULTRAPASSAGEM,
) -> CustoDemandaMensal:
    """Faturamento de demanda de um mês/posto (referência sintética).

    ``D_faturável = max(DC, D_med)``; ultrapassagem ``(D_med − DC)·2·T``
    quando ``D_med > 1,05·DC``; ociosidade ``max(DC − D_med, 0)``.
    """
    faturavel = max(dc, d_med)
    if d_med > (1.0 + tolerancia) * dc:
        ultrapassagem_kw = d_med - dc
    else:
        ultrapassagem_kw = 0.0
    ociosidade = max(dc - d_med, 0.0)
    custo = faturavel * tarifa + ultrapassagem_kw * fator_ultrapassagem * tarifa
    return CustoDemandaMensal(
        faturavel_kw=faturavel,
        ultrapassagem_kw=ultrapassagem_kw,
        ociosidade_kw=ociosidade,
        custo=custo,
    )


def _candidatos(dc_min: float, dc_max: float, passo: float) -> list[float]:
    if passo <= 0:
        raise ValueError("passo deve ser > 0")
    if dc_max < dc_min:
        raise ValueError("dc_max deve ser >= dc_min")
    n = int(math.floor((dc_max - dc_min) / passo + 1e-9)) + 1
    return [dc_min + i * passo for i in range(n)]


def _candidatos_breakpoints(
    medidas: Sequence[float], dc_min: float, dc_max: float
) -> list[float]:
    """Pontos de quebra exatos da função de custo anual (por posto).

    A função mensal é decrescente até ``D_med/1,05``, constante até
    ``D_med`` e crescente depois — o mínimo anual só pode ocorrer em
    ``dc_min`` ou em ``ceil(D_med/1,05)``/``D_med`` de algum mês.
    """
    pontos: set[float] = {float(dc_min)}
    for d in medidas:
        pontos.add(float(math.ceil(d / (1.0 + TOLERANCIA_ULTRAPASSAGEM))))
        pontos.add(float(d))
    return sorted(p for p in pontos if dc_min <= p <= dc_max)


def otimizar_contrato(
    medidas: Sequence[float],
    custo_fn: Callable[[float, int], CustoDemandaMensal],
    dc_min: float = DC_MINIMO_GRUPO_A,
    dc_max: float | None = None,
    passo: float | None = None,
) -> ResultadoContrato:
    """Otimiza a DC que minimiza o custo anual (1 variável).

    Args:
        medidas: demanda medida de cada mês (kW).
        custo_fn: ``custo_fn(dc, mes_idx) -> CustoDemandaMensal``.
        dc_min: mínimo regulatório (padrão 30 kW).
        dc_max: teto da busca; ``None`` = ``ceil(max(medidas) · 1,2)``.
        passo: ``None`` (padrão) avalia apenas os pontos de quebra
            (exato e rápido); um float faz a busca exaustiva nesse passo
            (usado nos testes de equivalência).

    Empate de custo resolve pela MENOR demanda contratada.
    """
    medidas = tuple(medidas)
    if not medidas:
        raise ValueError("medidas não pode ser vazio")
    if dc_max is None:
        dc_max = float(math.ceil(max(medidas) * 1.2))
    dc_max = max(dc_max, dc_min)

    if passo is None:
        candidatos = _candidatos_breakpoints(medidas, dc_min, dc_max)
    else:
        candidatos = _candidatos(dc_min, dc_max, passo)

    melhor_dc: float | None = None
    melhor_custo = float("inf")
    melhor_mensal: tuple[CustoDemandaMensal, ...] | None = None

    for dc in candidatos:
        mensal = tuple(custo_fn(dc, i) for i in range(len(medidas)))
        total = sum(m.custo for m in mensal)
        if total < melhor_custo - 1e-9 or (
            abs(total - melhor_custo) <= 1e-9 and dc < melhor_dc
        ):
            melhor_dc, melhor_custo, melhor_mensal = dc, total, mensal

    assert melhor_dc is not None and melhor_mensal is not None
    return ResultadoContrato(
        dc=melhor_dc,
        custo_anual=melhor_custo,
        custos_mensais=tuple(m.custo for m in melhor_mensal),
        faturavel_mensal=tuple(m.faturavel_kw for m in melhor_mensal),
        ultrapassagem_mensal=tuple(m.ultrapassagem_kw for m in melhor_mensal),
        ociosidade_mensal=tuple(m.ociosidade_kw for m in melhor_mensal),
    )


def _contrato_para_dc(
    dc: float,
    medidas: Sequence[float],
    custo_fn: Callable[[float, int], CustoDemandaMensal],
) -> ResultadoContrato:
    mensal = tuple(custo_fn(dc, i) for i in range(len(medidas)))
    return ResultadoContrato(
        dc=dc,
        custo_anual=sum(m.custo for m in mensal),
        custos_mensais=tuple(m.custo for m in mensal),
        faturavel_mensal=tuple(m.faturavel_kw for m in mensal),
        ultrapassagem_mensal=tuple(m.ultrapassagem_kw for m in mensal),
        ociosidade_mensal=tuple(m.ociosidade_kw for m in mensal),
    )


def otimizar_contrato_azul(
    medidas_ponta: Sequence[float],
    medidas_fora_ponta: Sequence[float],
    custo_posto_fn: Callable[[str, float, int], CustoDemandaMensal],
    dc_min: float = DC_MINIMO_GRUPO_A,
    dc_max: float | None = None,
    passo: float = PASSO_PADRAO,
) -> ResultadoContratoAzul:
    """Otimiza as duas DC da Azul (postos independentes, item B)."""
    ponta = otimizar_contrato(
        medidas_ponta,
        lambda dc, i: custo_posto_fn(POSTO_PONTA, dc, i),
        dc_min=dc_min,
        dc_max=dc_max,
        passo=passo,
    )
    fora = otimizar_contrato(
        medidas_fora_ponta,
        lambda dc, i: custo_posto_fn(POSTO_FORA_PONTA, dc, i),
        dc_min=dc_min,
        dc_max=dc_max,
        passo=passo,
    )
    return ResultadoContratoAzul(ponta=ponta, fora_ponta=fora)


# ---------------------------------------------------------------------------
# C) Demanda de ponta de equilíbrio
# ---------------------------------------------------------------------------


def demanda_ponta_equilibrio(
    custo_azul_fn: Callable[[float], float],
    custo_verde: float,
    d_med_unica: float,
    tolerancia_kw: float = TOLERANCIA_EQUILIBRIO_KW,
) -> ResultadoEquilibrio:
    """Calcula ``Dp_eq`` por bisseção (item C).

    ``custo_azul_fn(d_med_ponta)`` devolve o custo anual ótimo da Azul para
    a demanda de ponta informada (com ``Dfp = d_med_unica`` e DC_ponta
    otimizada a cada avaliação). O custo da Azul cresce com ``Dp``.
    """
    f0 = custo_azul_fn(0.0)
    if f0 > custo_verde:
        # Mesmo com Dp = 0 a Azul é mais cara → Verde sempre melhor.
        return ResultadoEquilibrio(
            dp_eq=None,
            mensagem=(
                "A modalidade Verde é mais vantajosa para qualquer demanda "
                "de ponta."
            ),
            verde_sempre_melhor=True,
        )
    fhi = custo_azul_fn(d_med_unica)
    if fhi <= custo_verde:
        # Mesmo com Dp = demanda única a Azul é mais barata → Azul sempre.
        return ResultadoEquilibrio(
            dp_eq=d_med_unica,
            mensagem=(
                "A modalidade Azul tende a ser mais vantajosa para qualquer "
                "demanda de ponta."
            ),
            azul_sempre_melhor=True,
        )

    lo, hi = 0.0, d_med_unica
    while hi - lo > tolerancia_kw:
        mid = (lo + hi) / 2.0
        if custo_azul_fn(mid) > custo_verde:
            hi = mid
        else:
            lo = mid
    dp_eq = (lo + hi) / 2.0
    return ResultadoEquilibrio(
        dp_eq=dp_eq,
        mensagem=(
            f"Se a sua demanda de ponta for menor que {dp_eq:.1f} kW, a "
            "modalidade Azul tende a ser mais vantajosa."
        ),
    )


# ---------------------------------------------------------------------------
# D) Comparação e decomposição do ganho
# ---------------------------------------------------------------------------


def decompor_ganho(
    custo_atual_contrato_atual: float,
    custo_atual_demanda_otima: float,
    custo_melhor_demanda_otima: float,
) -> GanhoComparacao:
    """Decompõe o ganho anual (item D)."""
    ganho_total = custo_atual_contrato_atual - custo_melhor_demanda_otima
    ganho_demanda = custo_atual_contrato_atual - custo_atual_demanda_otima
    return GanhoComparacao(
        ganho_total=ganho_total,
        ganho_demanda=ganho_demanda,
        ganho_modalidade=ganho_total - ganho_demanda,
    )


def comparar_planejamento(
    resultados: Sequence[ResultadoModalidadePlanejamento],
    modalidade_atual: str,
    avisos: Sequence[str] = (),
    equilibrio: ResultadoEquilibrio | None = None,
) -> ResultadoPlanejamento:
    """Monta a saída final da comparação (item D)."""
    resultados = tuple(resultados)
    if not resultados:
        raise ValueError("nenhuma modalidade para comparar")

    atual = next(
        (r for r in resultados if r.modalidade.upper() == modalidade_atual.upper()),
        resultados[0],
    )
    melhor_otim = min(resultados, key=lambda r: r.custo_demanda_otimizada)
    melhor_atual = min(resultados, key=lambda r: r.custo_contrato_atual)

    ganho = decompor_ganho(
        atual.custo_contrato_atual,
        atual.custo_demanda_otimizada,
        melhor_otim.custo_demanda_otimizada,
    )
    return ResultadoPlanejamento(
        modalidades=resultados,
        melhor_contrato_atual=melhor_atual.modalidade,
        melhor_demanda_otimizada=melhor_otim.modalidade,
        ganho=ganho,
        avisos=tuple(avisos),
        equilibrio=equilibrio,
    )
