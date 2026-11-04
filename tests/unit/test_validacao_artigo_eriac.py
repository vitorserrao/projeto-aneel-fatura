"""Validação contra o artigo XX ERIAC 2025 — Consumidor 1 (CPFL Piratininga).

Reproduz as linhas da Figura 6 do artigo para Horária Verde e Horária Azul com
o motor: tributos "por dentro" (PIS 1,35% + COFINS 6,20% + ICMS 18%),
ultrapassagem tributada e reativos no modo "excedente direto".

Observações registradas do artigo:
- o PIS impresso (1,55%) não fecha; os valores foram calculados com 1,35%;
- a demanda fora ponta impressa (289,27 kW) não fecha; foi calculada com
  283,27 kW (mesma da ponta);
- a TUSD Energia da Azul impressa (3.731,54) não soma com o total do artigo
  (o total exige ~3.734,52) — erro interno do artigo;
- a bandeira do artigo (906,43 / 905,43) usa taxa ~0,01175 R$/kWh que não está
  na nossa base (temos 0,010 R$/kWh) — por isso a bandeira fica FORA dos
  asserts abaixo;
- a tarifa de reativo do artigo (~0,37881 R$/kVArh, implícita em R$ 14,91) NÃO
  é usada: o projeto calcula TE B1 Residencial/1000 (0,28209 para CPFL 05/2018),
  divergindo dos R$ 14,91 publicados (decisão: tarifa calculada, não derivada).
"""

from __future__ import annotations

from datetime import date

import pytest

from core.motor_calculo import calcular_fatura
from core.models import Consumidor
from core.tarifas import ParcelaTarifaria

PIS, COFINS, ICMS = 0.0135, 0.062, 0.18
TARIFA_REATIVO_ENERGIA = 0.28209  # R$/kVArh — calculada: TE B1 Residencial/1000 (282,09/1000) CPFL 05/2018


def _consumidor(**over):
    base = dict(
        distribuidora="CPFL-PIRATINING",
        subgrupo="A4",
        classe="Não se aplica",
        data_referencia=date(2018, 5, 28),
        detalhe="Não se aplica",
        consumo_ponta_kwh=8_849.85,
        consumo_fora_ponta_kwh=68_276.07,
        demanda_ponta_kw=283.27,
        demanda_fora_ponta_kw=283.27,
        demanda_contratada_ponta_kw=200.0,
        demanda_contratada_fora_ponta_kw=200.0,
        demanda_medida_unica_kw=283.27,
        demanda_contratada_unica_kw=200.0,
        reativo_energia_fora_ponta_kvArh=39.36,  # excedente pronto (modo direto)
        cip_cosip_rs=60.0,
    )
    base.update(over)
    return Consumidor(**base)


def _parcelas_azul():
    return [
        ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 20.54),
        ParcelaTarifaria("TUSD", "DEMANDA", "FORA PONTA", "R$/kW", 9.90),
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 36.04),
        ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 36.04),
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 417.66),
        ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 269.77),
    ]


def _parcelas_verde():
    return [
        ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 9.90),
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 534.52),
        ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 36.04),
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 417.66),
        ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 269.77),
    ]


def _fatura(modalidade, parcelas, demanda_unica):
    return calcular_fatura(
        _consumidor(),
        modalidade,
        parcelas,
        demanda_unica=demanda_unica,
        aplicar_tributos=True,
        pis=PIS,
        cofins=COFINS,
        icms=ICMS,
        tipo_icms="dentro",
        reativos_direto=True,
        tarifa_reativo_energia_r_kvarh=TARIFA_REATIVO_ENERGIA,
        arredondar_centavos=True,
    )


def test_artigo_verde_linhas_principais():
    fatura = _fatura("Verde", _parcelas_verde(), demanda_unica=True)

    demanda = [l for l in fatura.linhas if l.categoria == "TARIFA" and l.descricao.startswith("TUSD DEMANDA")]
    assert len(demanda) == 1
    assert demanda[0].custo == pytest.approx(3_766.77, abs=0.05)

    tusd_e = sum(
        l.custo for l in fatura.linhas if l.descricao.startswith("TUSD ENERGIA")
    )
    assert tusd_e == pytest.approx(9_658.95, abs=0.05)

    te = sum(l.custo for l in fatura.linhas if l.descricao.startswith("TE ENERGIA"))
    assert te == pytest.approx(29_704.59, abs=0.05)

    up = [l for l in fatura.linhas if l.categoria == "ULTRAPASSAGEM"]
    assert len(up) == 1
    assert up[0].custo == pytest.approx(2_214.54, abs=0.05)

    reat = [l for l in fatura.linhas if l.categoria == "REATIVOS"]
    assert len(reat) == 1
    assert reat[0].custo == pytest.approx(39.36 * TARIFA_REATIVO_ENERGIA, abs=0.01)

    # Total sem bandeira = total do artigo (46.326,20) − bandeira do artigo (906,43).
    assert fatura.custo_total == pytest.approx(46_326.20 - 906.43 - 14.91 + 39.36 * TARIFA_REATIVO_ENERGIA, abs=0.10)


def test_artigo_azul_linhas_principais():
    fatura = _fatura("Azul", _parcelas_azul(), demanda_unica=False)

    demanda = sum(
        l.custo for l in fatura.linhas if l.descricao.startswith("TUSD DEMANDA")
    )
    assert demanda == pytest.approx(11_581.88, abs=0.05)

    tusd_e = sum(
        l.custo for l in fatura.linhas if l.descricao.startswith("TUSD ENERGIA")
    )
    # O artigo imprime 3.731,54 e o total dele exige ~3.734,52 (erro interno
    # do artigo). O valor aritmético com as tarifas publicadas é 3.733,54 —
    # que é o que o motor reproduz após arredondar por linha.
    assert tusd_e == pytest.approx(3_733.54, abs=0.01)

    te = sum(l.custo for l in fatura.linhas if l.descricao.startswith("TE ENERGIA"))
    assert te == pytest.approx(29_704.58, abs=0.05)

    up = sum(l.custo for l in fatura.linhas if l.categoria == "ULTRAPASSAGEM")
    # 6.809,24 vs 6.809,18: +0,06 de arredondamento interno do artigo.
    assert up == pytest.approx(6_809.18, abs=0.10)

    reat = [l for l in fatura.linhas if l.categoria == "REATIVOS"]
    assert len(reat) == 1
    assert reat[0].custo == pytest.approx(39.36 * TARIFA_REATIVO_ENERGIA, abs=0.01)

    assert fatura.custo_total == pytest.approx(52_810.50 - 905.43 - 14.91 + 39.36 * TARIFA_REATIVO_ENERGIA, abs=1.0)


def test_ultrapassagem_nao_tributada_sem_aplicar_tributos():
    fatura = calcular_fatura(
        _consumidor(),
        "Verde",
        _parcelas_verde(),
        demanda_unica=True,
        reativos_direto=True,
        tarifa_reativo_energia_r_kvarh=TARIFA_REATIVO_ENERGIA,
    )
    up = [l for l in fatura.linhas if l.categoria == "ULTRAPASSAGEM"]
    assert len(up) == 1
    assert up[0].custo == pytest.approx(1_648.75, abs=0.01)


def test_reativos_direto_sem_tarifa_nao_gera_linhas():
    fatura = calcular_fatura(
        _consumidor(),
        "Verde",
        _parcelas_verde(),
        demanda_unica=True,
        reativos_direto=True,
    )
    assert not [l for l in fatura.linhas if l.categoria == "REATIVOS"]


def test_reativos_direto_demanda():
    fatura = calcular_fatura(
        _consumidor(reativo_energia_fora_ponta_kvArh=0.0, reativo_demanda_fora_ponta_kvAr=5.0),
        "Verde",
        _parcelas_verde(),
        demanda_unica=True,
        reativos_direto=True,
        tarifa_reativo_demanda_r_kvar=0.5,
    )
    reat = [l for l in fatura.linhas if l.categoria == "REATIVOS"]
    assert len(reat) == 1
    assert reat[0].quantidade == 5.0
    assert reat[0].custo == pytest.approx(2.5, abs=1e-12)
