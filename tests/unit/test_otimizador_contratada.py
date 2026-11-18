"""Testes do otimizador de demanda contratada (sprint Verde × Azul)."""

from datetime import date

import pytest

from core.otimizador import (
    demanda_verde_mensal,
    faixa_demanda_ponta,
    horas_ponta,
    otimizar_contratada,
)

DP = [
    29.12, 12.60, 19.04, 17.92, 16.24, 45.64,
    22.12, 31.36, 17.92, 8.40, 5.88, 4.48,
]
DFP = [
    41.44, 17.08, 24.36, 26.60, 29.12, 80.08,
    27.16, 31.36, 21.28, 40.60, 31.08, 35.00,
]
EP = [
    441.00, 323.96, 423.29, 518.00, 498.68, 420.91,
    488.18, 752.22, 347.06, 257.39, 234.85, 142.38,
]
EFP = [
    1834.56, 1572.06, 1709.12, 1877.47, 2179.59, 2962.12,
    4092.76, 5916.40, 4414.55, 5982.76, 4380.32, 2650.48,
]


def test_fatura_real_12_meses_ponta():
    dc, custo = otimizar_contratada(DP, piso=30.0, tolerancia=0.05, fator=2.0)
    assert dc == pytest.approx(30.0)
    assert custo == pytest.approx(408.28, abs=1e-6)


def test_fatura_real_12_meses_fora_ponta():
    dc, custo = otimizar_contratada(DFP, piso=30.0, tolerancia=0.05, fator=2.0)
    assert dc == pytest.approx(35.00 / 1.05)
    assert custo == pytest.approx(588.03, abs=0.01)


def test_fatura_real_12_meses_verde_segue_fora_ponta():
    d_verde = [max(dp, dfp) for dp, dfp in zip(DP, DFP)]
    assert all(d_verde[i] == DFP[i] for i in range(len(DP)))

    dc_p, _ = otimizar_contratada(DP, 30.0, 0.05, 2.0)
    dc_fp, _ = otimizar_contratada(DFP, 30.0, 0.05, 2.0)
    dc_verde, _ = otimizar_contratada(d_verde, 30.0, 0.05, 2.0)
    assert dc_verde == pytest.approx(dc_fp)
    assert dc_verde != pytest.approx(dc_p)


def test_faixa_dez_isolado_horas_ponta_63():
    # min = Ep/hp = 441/63 = 7,0 (o piso de 30 kW é da CONTRATADA, não entra
    # na faixa da demanda medida).
    assert faixa_demanda_ponta(441.0, 63.0, 41.44) == pytest.approx(
        (7.0, 41.44)
    )


def test_faixa_minimo_e_media_da_ponta_quando_acima_do_piso():
    minimo, maximo = faixa_demanda_ponta(2000.0, 63.0, 41.44)
    assert minimo == pytest.approx(2000.0 / 63.0)
    assert maximo == pytest.approx(41.44)


def test_faixa_demanda_abaixo_de_30_nao_quebra():
    # Mês com D_verde < 30 kW: a faixa é [Ep/hp, D_verde] e não inverte.
    minimo, maximo = faixa_demanda_ponta(200.0, 63.0, 17.08)
    assert minimo == pytest.approx(200.0 / 63.0)
    assert maximo == pytest.approx(17.08)


def test_faixa_exige_horas_positivas():
    with pytest.raises(ValueError):
        faixa_demanda_ponta(441.0, 0.0, 41.44)


def test_demanda_verde_mensal_max_dos_postos():
    assert demanda_verde_mensal(10.0, 20.0) == 20.0
    assert demanda_verde_mensal(20.0, 10.0) == 20.0


def test_demanda_verde_mensal_none_nao_vira_zero():
    assert demanda_verde_mensal(None, 20.0) == 20.0
    assert demanda_verde_mensal(20.0, None) == 20.0
    with pytest.raises(ValueError):
        demanda_verde_mensal(None, None)


def test_horas_ponta_dias_uteis_do_ciclo():
    # segunda a segunda: 5 dias úteis no ciclo (ter–seg) × 3 h = 15 h.
    assert horas_ponta(
        date(2025, 1, 6), date(2025, 1, 13), (), 3.0
    ) == pytest.approx(15.0)


def test_horas_ponta_exclui_feriado():
    # 09/01/2025 (quinta) é feriado informado → 4 dias úteis × 3 h = 12 h.
    assert horas_ponta(
        date(2025, 1, 6),
        date(2025, 1, 13),
        (date(2025, 1, 9),),
        3.0,
    ) == pytest.approx(12.0)


def test_horas_ponta_nao_aceita_ciclo_invertido():
    with pytest.raises(ValueError):
        horas_ponta(date(2025, 1, 13), date(2025, 1, 6), (), 3.0)


def test_otimizar_contratada_recusa_lista_vazia():
    with pytest.raises(ValueError):
        otimizar_contratada([], 30.0, 0.05, 2.0)

