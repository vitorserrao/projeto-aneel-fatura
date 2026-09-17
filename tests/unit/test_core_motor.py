"""Testes unitários do motor de cálculo determinístico (core/motor_calculo.py)."""

import pytest

from core.models import Consumidor
from core.motor_calculo import (
    UnidadeTarifariaNaoSuportada,
    calcular_custo_acr,
    calcular_parcela,
)
from core.tarifas import ParcelaTarifaria


def _consumidor(**overrides):
    base = dict(
        distribuidora="DIST",
        subgrupo="A4",
        classe="COMERCIAL",
        consumo_ponta_kwh=1000.0,
        consumo_fora_ponta_kwh=9000.0,
        demanda_ponta_kw=50.0,
        demanda_fora_ponta_kw=100.0,
    )
    base.update(overrides)
    return Consumidor(**base)


def _calc(modalidade="AZUL", **consumidor_overrides):
    consumidor = _consumidor(**consumidor_overrides)
    parcelas = [
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 300.0),
        ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 200.0),
        ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 40.0),
        ParcelaTarifaria("TUSD", "DEMANDA", "FORA PONTA", "R$/kW", 20.0),
    ]
    return calcular_custo_acr(consumidor, modalidade, parcelas)


# --- Parcela individual -----------------------------------------------------

def test_parcela_energia_converte_kwh_para_mwh():
    consumidor = _consumidor(consumo_ponta_kwh=1500.0)
    parcela = ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 300.0)
    resultado = calcular_parcela(parcela, consumidor)
    assert resultado.quantidade == 1.5
    assert resultado.custo == 450.0


def test_parcela_energia_em_kwh_nao_converte():
    consumidor = _consumidor(consumo_ponta_kwh=1500.0)
    parcela = ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/kWh", 0.3)
    resultado = calcular_parcela(parcela, consumidor)
    assert resultado.quantidade == 1500.0
    assert resultado.custo == pytest.approx(450.0)


def test_parcela_demanda_usa_kw_direto():
    consumidor = _consumidor(demanda_ponta_kw=80.0)
    parcela = ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 40.0)
    resultado = calcular_parcela(parcela, consumidor)
    assert resultado.quantidade == 80.0
    assert resultado.custo == 3200.0


@pytest.mark.parametrize(
    "grandeza,unidade",
    [
        ("ENERGIA", "R$/kW"),      # unidade incompatível com energia
        ("DEMANDA", "R$/MWh"),     # unidade incompatível com demanda
        ("DEMANDA", "R$/kWh"),
    ],
)
def test_unidade_incompativel_lanca_erro(grandeza, unidade):
    consumidor = _consumidor()
    parcela = ParcelaTarifaria("TUSD", grandeza, "PONTA", unidade, 10.0)
    with pytest.raises(UnidadeTarifariaNaoSuportada):
        calcular_parcela(parcela, consumidor)


# --- Cálculo integral -------------------------------------------------------

def test_custo_total_soma_todas_as_parcelas():
    resultado = _calc()
    assert resultado.custo_total == pytest.approx(
        1000 * 0.001 * 300          # TE energia ponta
        + 9000 * 0.001 * 200        # TE energia fora ponta
        + 50 * 40                   # TUSD demanda ponta
        + 100 * 20                  # TUSD demanda fora ponta
    )
    # 300 + 1800 + 2000 + 2000 = 6100
    assert resultado.custo_total == pytest.approx(6100.0)


def test_totais_por_componente_e_grandeza():
    resultado = _calc()
    assert resultado.custo_te == pytest.approx(2100.0)
    assert resultado.custo_tusd == pytest.approx(4000.0)
    assert resultado.custo_energia == pytest.approx(2100.0)
    assert resultado.custo_demanda == pytest.approx(4000.0)


def test_determinismo_mesmas_entradas_mesmo_resultado():
    r1 = _calc()
    r2 = _calc()
    assert r1 == r2
    assert r1.custo_total == r2.custo_total


def test_modalidade_vazia_lanca_erro():
    consumidor = _consumidor()
    parcelas = [ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 300.0)]
    with pytest.raises(ValueError):
        calcular_custo_acr(consumidor, " ", parcelas)


def test_nenhuma_parcela_lanca_erro():
    consumidor = _consumidor()
    with pytest.raises(ValueError):
        calcular_custo_acr(consumidor, "AZUL", [])
