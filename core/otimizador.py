"""Otimizador de modalidades tarifárias aplicáveis.

Implementa apenas ordenação determinística de custos: compara modalidades já
calculadas pelo motor e seleciona a de menor custo total, com desempate
estável (ordem de chegada).

Nenhum critério regulatório de elegibilidade (quais modalidades se aplicam a
um consumidor — azul, verde, convencional, branca — e em que condições) é
assumido: essa determinação permanece pendente (docs/premissas.md, P3/P4).
O que o core garante é que, dadas as modalidades calculadas, a escolha de
menor custo é determinística.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

from .models import ResultadoCalculo, ResultadoOtimizacao


# ---------------------------------------------------------------------------
# Otimização da demanda contratada e estimativas de ponta (sprint Verde × Azul)
# ---------------------------------------------------------------------------
# Funções puras: recebem todos os parâmetros regulatórios por argumento e não
# importam configuração nem infraestrutura.


def otimizar_contratada(
    demandas_medidas: list[float],
    piso: float,
    tolerancia: float,
    fator: float,
) -> tuple[float, float]:
    """Otimiza a demanda contratada que minimiza o custo em kW·mês.

    O custo independe da tarifa (que é um fator multiplicativo):

        C(Dc) = Σ_m [ max(D_m, Dc) + fator·(D_m − Dc)
                      se D_m > (1 + tolerancia)·Dc ]

    Candidatos: ``{piso} ∪ {D_m} ∪ {D_m/(1+tolerancia)}``, filtrando valores
    ``≥ piso``. Em caso de empate, vence a MENOR demanda contratada
    (determinístico).

    Returns:
        ``(dc_otima, custo_em_kw_mes)``.
    """
    demandas = [float(d) for d in demandas_medidas]
    if not demandas:
        raise ValueError("demandas_medidas não pode ser vazio")
    if piso < 0:
        raise ValueError("piso não pode ser negativo")
    if tolerancia < 0:
        raise ValueError("tolerancia não pode ser negativa")
    if fator < 0:
        raise ValueError("fator não pode ser negativo")

    candidatos: set[float] = {float(piso)}
    for d in demandas:
        candidatos.add(d)
        candidatos.add(d / (1.0 + tolerancia))
    ordenados = sorted(c for c in candidatos if c >= piso - 1e-12)
    if not ordenados:
        ordenados = [float(piso)]

    def custo(dc: float) -> float:
        total = 0.0
        for d in demandas:
            total += max(d, dc)
            if d > (1.0 + tolerancia) * dc:
                total += fator * (d - dc)
        return total

    melhor_dc = ordenados[0]
    melhor_custo = custo(melhor_dc)
    for dc in ordenados[1:]:
        custo_dc = custo(dc)
        if custo_dc < melhor_custo - 1e-9 or (
            abs(custo_dc - melhor_custo) <= 1e-9 and dc < melhor_dc
        ):
            melhor_dc = dc
            melhor_custo = custo_dc
    return melhor_dc, melhor_custo


def demanda_verde_mensal(dp: float | None, dfp: float | None) -> float:
    """Demanda da Verde no mês: ``max(Dp, Dfp)`` quando os dois postos existem.

    ``None`` = dado ausente e NUNCA vira zero. Se apenas um posto existir, ele
    é usado; se nenhum existir, a função recusa (a camada de serviço decide
    excluir o mês ou emitir aviso).
    """
    if dp is None and dfp is None:
        raise ValueError("demanda da Verde exige ao menos um dos postos (dp, dfp)")
    if dp is None:
        return float(dfp)
    if dfp is None:
        return float(dp)
    return max(float(dp), float(dfp))


def faixa_demanda_ponta(
    ep_kwh: float,
    horas_ponta: float,
    d_verde: float,
    piso: float,
) -> tuple[float, float]:
    """Faixa possível para a demanda de ponta da Azul a partir da fatura Verde.

    - ``min = max(Ep / horas_ponta, piso)``: a demanda média na ponta é um
      piso físico — o pico nunca é menor que a média.
    - ``max = D_verde``: a demanda medida da Verde é o pico do mês inteiro.

    ``None``/valores inconsistentes geram ``ValueError`` (nunca viram zero).
    """
    if ep_kwh is None or horas_ponta is None or d_verde is None:
        raise ValueError("ep_kwh, horas_ponta e d_verde são obrigatórios")
    if horas_ponta <= 0:
        raise ValueError("horas_ponta deve ser maior que 0")
    minimo = max(float(ep_kwh) / float(horas_ponta), float(piso))
    maximo = float(d_verde)
    if maximo < minimo:
        raise ValueError(
            f"faixa de demanda de ponta inconsistente: D_verde ({maximo}) "
            f"menor que o mínimo ({minimo})"
        )
    return minimo, maximo


def horas_ponta(
    data_leitura_anterior: date,
    data_leitura_atual: date,
    feriados: Iterable[date],
    horas_por_dia: float,
) -> float:
    """Horas de ponta no ciclo de leitura.

    Conta os dias úteis (sem sábados, domingos e feriados nacionais) no
    intervalo ``(anterior, atual]`` — os dias efetivamente faturados no ciclo
    — e multiplica por ``horas_por_dia``. A lista de feriados é recebida por
    parâmetro para o core continuar puro.
    """
    if not isinstance(data_leitura_anterior, date) or not isinstance(
        data_leitura_atual, date
    ):
        raise ValueError("datas de leitura devem ser objetos date")
    if data_leitura_atual <= data_leitura_anterior:
        raise ValueError(
            "data_leitura_atual deve ser posterior a data_leitura_anterior"
        )
    if horas_por_dia <= 0:
        raise ValueError("horas_por_dia deve ser maior que 0")

    feriados_set = {
        f if isinstance(f, date) else date.fromisoformat(str(f)) for f in feriados
    }
    dias_uteis = 0
    dia = data_leitura_anterior + timedelta(days=1)
    while dia <= data_leitura_atual:
        if dia.weekday() < 5 and dia not in feriados_set:
            dias_uteis += 1
        dia += timedelta(days=1)
    return float(dias_uteis) * float(horas_por_dia)



def otimizar_modalidade(
    resultados: Iterable[ResultadoCalculo],
) -> ResultadoOtimizacao:
    """Seleciona a modalidade de menor custo total entre as calculadas.

    Args:
        resultados: resultados de cálculo, um por modalidade candidata.

    Returns:
        ResultadoOtimizacao com ``modalidade_escolhida``, ranking crescente de
        custo, indicador de empate e economia em relação ao segundo colocado.

    Raises:
        ValueError: nenhum resultado fornecido.
    """
    lista = list(resultados)
    if not lista:
        raise ValueError("nenhum resultado de cálculo fornecido")

    # sorted com key (custo_total, índice): empate resolve pela ordem de
    # chegada, garantindo determinismo (nunca nativo de dict).
    ranking = tuple(
        sorted(
            enumerate(lista),
            key=lambda par: (par[1].custo_total, par[0]),
        )
    )

    primeiro = ranking[0][1]
    empate = (
        len(ranking) > 1
        and ranking[1][1].custo_total == primeiro.custo_total
    )
    economia_vs_segunda = 0.0
    if len(ranking) > 1:
        economia_vs_segunda = ranking[1][1].custo_total - primeiro.custo_total

    return ResultadoOtimizacao(
        modalidade_escolhida=primeiro.modalidade,
        ranking=tuple(res for _, res in ranking),
        empate=empate,
        economia_vs_segunda=economia_vs_segunda,
    )
