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

from typing import Iterable

from .models import ResultadoCalculo, ResultadoOtimizacao


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
