"""Testes unitários do otimizador de modalidades (core/otimizador.py)."""

import pytest

from core.models import ParcelaCusto, ResultadoCalculo
from core.otimizador import otimizar_modalidade


def _resultado(modalidade, custo_total):
    return ResultadoCalculo(
        modalidade=modalidade,
        parcelas=(ParcelaCusto("TUSD", "DEMANDA", "PONTA", 0.0, 0.0, custo_total),),
    )


def test_escolhe_modalidade_de_menor_custo():
    azul = _resultado("AZUL", 5000.0)
    verde = _resultado("VERDE", 4500.0)
    resultado = otimizar_modalidade([azul, verde])
    assert resultado.modalidade_escolhida == "VERDE"
    assert resultado.empate is False
    assert resultado.economia_vs_segunda == pytest.approx(500.0)


def test_ordena_ranking_por_custo_crescente():
    a = _resultado("A", 30.0)
    b = _resultado("B", 10.0)
    c = _resultado("C", 20.0)
    resultado = otimizar_modalidade([a, b, c])
    assert [r.modalidade for r in resultado.ranking] == ["B", "C", "A"]


def test_empate_detectado_e_desempate_estavel():
    x = _resultado("X", 100.0)
    y = _resultado("Y", 100.0)
    resultado = otimizar_modalidade([x, y])
    assert resultado.empate is True
    # Empate em custo: mantém a ordem de chegada (determinístico).
    assert resultado.modalidade_escolhida == "X"
    assert resultado.economia_vs_segunda == 0.0


def test_sem_resultados_lanca_erro():
    with pytest.raises(ValueError):
        otimizar_modalidade([])


def test_unico_resultado_e_eleito_sem_empate():
    unico = _resultado("AZUL", 4000.0)
    resultado = otimizar_modalidade([unico])
    assert resultado.modalidade_escolhida == "AZUL"
    assert resultado.empate is False
    assert resultado.economia_vs_segunda == 0.0
