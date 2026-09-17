"""Testa a demanda única da modalidade Verde (REN 1.000/2021)."""

from datetime import date

from core.motor_calculo import calcular_fatura
from core.models import Consumidor
from core.tarifas import ParcelaTarifaria


def _consumidor(medida_unica=180.0, contratada_unica=200.0):
    return Consumidor(
        distribuidora="DIST",
        subgrupo="A4",
        classe="Não se aplica",
        data_referencia=date(2024, 1, 1),
        detalhe="Não se aplica",
        consumo_ponta_kwh=1000.0,
        consumo_fora_ponta_kwh=2000.0,
        # P/FP só para modalidades horárias (Azul); a Verde ignora.
        demanda_ponta_kw=100.0,
        demanda_fora_ponta_kw=300.0,
        demanda_contratada_ponta_kw=120.0,
        demanda_contratada_fora_ponta_kw=180.0,
        demanda_medida_unica_kw=medida_unica,
        demanda_contratada_unica_kw=contratada_unica,
    )


def _parcela_demanda_verde():
    # Tarifa de demanda única da Verde (posto normalizado PONTA pelo service).
    return [ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 50.0)]


def test_demanda_unique_verde_usa_max_medida_contratada():
    # medida única 180 < contratada única 200 -> faturável = 200
    fatura = calcular_fatura(
        _consumidor(), "Verde", _parcela_demanda_verde(), demanda_unica=True
    )
    demanda = [l for l in fatura.linhas if l.descricao == "TUSD DEMANDA PONTA"]
    assert len(demanda) == 1
    assert abs(demanda[0].quantidade - 200.0) < 1e-9


def test_demanda_unica_verde_ignora_p_fp():
    # A demanda P/FP (100/300) NÃO pode influenciar a Verde: mesmo com FP=300
    # e contratada FP=180, o resultado deve usar só os campos únicos (200).
    fatura = calcular_fatura(
        _consumidor(), "Verde", _parcela_demanda_verde(), demanda_unica=True
    )
    demanda = [l for l in fatura.linhas if l.descricao == "TUSD DEMANDA PONTA"]
    assert abs(demanda[0].quantidade - 200.0) < 1e-9


def test_demanda_unica_medida_maior():
    # medida única 250 > contratada única 200 -> faturável = 250
    fatura = calcular_fatura(
        _consumidor(medida_unica=250.0), "Verde", _parcela_demanda_verde(),
        demanda_unica=True,
    )
    demanda = [l for l in fatura.linhas if l.descricao == "TUSD DEMANDA PONTA"]
    assert abs(demanda[0].quantidade - 250.0) < 1e-9


def test_ultrapassagem_verde_usa_campos_unicos():
    # medida única 250 > contratada única 200 × 1.05 (210) -> gatilho OK.
    # excedente total = 250 - 200 = 50; tarifa demanda única = 50 -> 2x = 100.
    fatura = calcular_fatura(
        _consumidor(medida_unica=250.0), "Verde", _parcela_demanda_verde(),
        demanda_unica=True,
    )
    ult = [l for l in fatura.linhas if l.categoria == "ULTRAPASSAGEM"]
    assert len(ult) == 1
    assert abs(ult[0].quantidade - 50.0) < 1e-9
    assert abs(ult[0].tarifa - 100.0) < 1e-9
    assert abs(ult[0].custo - 5000.0) < 1e-9
