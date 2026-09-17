"""Testa as duas fórmulas de tributação (ICMS por dentro e por fora)."""

from datetime import date

from core.motor_calculo import calcular_fatura
from core.models import Consumidor
from core.tarifas import ParcelaTarifaria


def _consumidor():
    return Consumidor(
        distribuidora="DIST",
        subgrupo="A4",
        classe="Não se aplica",
        data_referencia=date(2024, 1, 1),
        detalhe="Não se aplica",
        consumo_ponta_kwh=1000.0,
        consumo_fora_ponta_kwh=2000.0,
        demanda_ponta_kw=100.0,
        demanda_fora_ponta_kw=200.0,
        demanda_contratada_ponta_kw=120.0,
        demanda_contratada_fora_ponta_kw=180.0,
    )


def _parcelas():
    return [
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 300.0),
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 400.0),
    ]


def test_tributos_dentro_aditivo():
    pis, cofins, icms = 0.0065, 0.03, 0.18
    base = calcular_fatura(_consumidor(), "Azul", _parcelas())
    com = calcular_fatura(
        _consumidor(), "Azul", _parcelas(),
        aplicar_tributos=True, pis=pis, cofins=cofins, icms=icms,
        tipo_icms="dentro",
    )
    fator = 1.0 / (1.0 - pis - cofins - icms)
    assert abs(com.custo_tarifas / base.custo_tarifas - fator) < 1e-9


def test_tributos_fora_multiplicativo():
    pis, cofins, icms = 0.0065, 0.03, 0.18
    base = calcular_fatura(_consumidor(), "Azul", _parcelas())
    com = calcular_fatura(
        _consumidor(), "Azul", _parcelas(),
        aplicar_tributos=True, pis=pis, cofins=cofins, icms=icms,
        tipo_icms="fora",
    )
    # Tarifa Homologada / ([1−(PIS+COFINS)/100] × [1−ICMS/100])  (fração)
    fator = 1.0 / ((1.0 - pis - cofins) * (1.0 - icms))
    assert abs(com.custo_tarifas / base.custo_tarifas - fator) < 1e-9


def test_tipo_icms_invalido():
    import pytest
    with pytest.raises(ValueError):
        calcular_fatura(
            _consumidor(), "Azul", _parcelas(),
            aplicar_tributos=True, pis=0.01, cofins=0.01, icms=0.1,
            tipo_icms="errado",
        )
