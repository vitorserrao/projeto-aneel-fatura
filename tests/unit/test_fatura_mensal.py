"""Testes da separação da demanda faturada (Súmula 391) em fatura_verde/fatura_azul."""

import pytest

from core.motor_calculo import (
    demanda_faturada_separada,
    fatura_azul,
    fatura_verde,
)


def test_separacao_medida_acima_da_contratada():
    # faturada = 103; utilizada = 103; não utilizada = 0.
    assert demanda_faturada_separada(103.0, 100.0) == pytest.approx(
        (103.0, 103.0, 0.0)
    )


def test_separacao_medida_abaixo_da_contratada():
    # faturada = 100; utilizada = 80; não utilizada = 20.
    assert demanda_faturada_separada(80.0, 100.0) == pytest.approx(
        (100.0, 80.0, 20.0)
    )


def test_fatura_verde_medida_103_contratada_100():
    # Caso obrigatório: utilizada 103, não utilizada 0, ultrapassagem 0
    # (103 não excede 100 × 1,05).
    fatura = fatura_verde(
        demanda_medida_unica_kw=103.0,
        demanda_contratada_unica_kw=100.0,
        consumo_ponta_kwh=0.0,
        consumo_fora_ponta_kwh=0.0,
        tarifa_tusd_demanda_r_kw=10.0,
        tarifa_tusd_energia_ponta_r_mwh=0.0,
        tarifa_tusd_energia_fora_ponta_r_mwh=0.0,
        tarifa_te_energia_ponta_r_mwh=0.0,
        tarifa_te_energia_fora_ponta_r_mwh=0.0,
        tolerancia=0.05,
        fator_ultrapassagem=2.0,
        pis=0.0,
        cofins=0.0,
        icms=0.0,
    )
    assert fatura.tusd_demanda == pytest.approx(103.0 * 10.0)
    assert fatura.ultrapassagem == pytest.approx(0.0)


def test_fatura_verde_nao_utilizada_so_pis_cofins():
    # medida 80 < contratada 100: 80 kW com ICMS e 20 kW só PIS/COFINS.
    pis, cofins, icms = 0.0095, 0.0438, 0.18
    fator_cheio = 1.0 / ((1.0 - pis - cofins) * (1.0 - icms))
    fator_isento = 1.0 / (1.0 - pis - cofins)
    fatura = fatura_verde(
        demanda_medida_unica_kw=80.0,
        demanda_contratada_unica_kw=100.0,
        consumo_ponta_kwh=0.0,
        consumo_fora_ponta_kwh=0.0,
        tarifa_tusd_demanda_r_kw=10.0,
        tarifa_tusd_energia_ponta_r_mwh=0.0,
        tarifa_tusd_energia_fora_ponta_r_mwh=0.0,
        tarifa_te_energia_ponta_r_mwh=0.0,
        tarifa_te_energia_fora_ponta_r_mwh=0.0,
        tolerancia=0.05,
        fator_ultrapassagem=2.0,
        pis=pis,
        cofins=cofins,
        icms=icms,
    )
    esperado = (80.0 * fator_cheio + 20.0 * fator_isento) * 10.0
    assert fatura.tusd_demanda == pytest.approx(esperado)


def test_fatura_azul_separa_por_posto():
    # Ponta: medida 103 > contratada 100 → 103 kW com ICMS, sem não utilizada.
    # Fora ponta: medida 80 < contratada 100 → 80 com ICMS + 20 isentos.
    pis, cofins, icms = 0.0095, 0.0438, 0.18
    fator_cheio = 1.0 / ((1.0 - pis - cofins) * (1.0 - icms))
    fator_isento = 1.0 / (1.0 - pis - cofins)
    fatura = fatura_azul(
        demanda_ponta_kw=103.0,
        demanda_fora_ponta_kw=80.0,
        demanda_contratada_ponta_kw=100.0,
        demanda_contratada_fora_ponta_kw=100.0,
        consumo_ponta_kwh=0.0,
        consumo_fora_ponta_kwh=0.0,
        tarifa_tusd_demanda_ponta_r_kw=30.0,
        tarifa_tusd_demanda_fora_ponta_r_kw=15.0,
        tarifa_tusd_energia_ponta_r_mwh=0.0,
        tarifa_tusd_energia_fora_ponta_r_mwh=0.0,
        tarifa_te_energia_ponta_r_mwh=0.0,
        tarifa_te_energia_fora_ponta_r_mwh=0.0,
        tolerancia=0.05,
        fator_ultrapassagem=2.0,
        pis=pis,
        cofins=cofins,
        icms=icms,
    )
    assert fatura.tusd_demanda_ponta == pytest.approx(103.0 * 30.0 * fator_cheio)
    assert fatura.tusd_demanda_fora_ponta == pytest.approx(
        (80.0 * fator_cheio + 20.0 * fator_isento) * 15.0
    )
    assert fatura.ultrapassagem == pytest.approx(0.0)


def test_flag_icms_demanda_nao_utilizada_true_reverte_isencao():
    pis, cofins, icms = 0.0095, 0.0438, 0.18
    fator_cheio = 1.0 / ((1.0 - pis - cofins) * (1.0 - icms))
    fatura = fatura_verde(
        demanda_medida_unica_kw=80.0,
        demanda_contratada_unica_kw=100.0,
        consumo_ponta_kwh=0.0,
        consumo_fora_ponta_kwh=0.0,
        tarifa_tusd_demanda_r_kw=10.0,
        tarifa_tusd_energia_ponta_r_mwh=0.0,
        tarifa_tusd_energia_fora_ponta_r_mwh=0.0,
        tarifa_te_energia_ponta_r_mwh=0.0,
        tarifa_te_energia_fora_ponta_r_mwh=0.0,
        tolerancia=0.05,
        fator_ultrapassagem=2.0,
        pis=pis,
        cofins=cofins,
        icms=icms,
        icms_demanda_nao_utilizada=True,
    )
    assert fatura.tusd_demanda == pytest.approx(100.0 * 10.0 * fator_cheio)
