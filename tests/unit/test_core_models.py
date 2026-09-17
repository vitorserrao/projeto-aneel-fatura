"""Testes unitários dos modelos de domínio do core."""

import pytest

from core.models import (
    GRANDEZA_DEMANDA,
    GRANDEZA_ENERGIA,
    Consumidor,
    ParcelaCusto,
    ResultadoCalculo,
)


def _consumidor_valido(**overrides):
    base = dict(
        distribuidora="DISTRIBUIDORA X",
        subgrupo="A4",
        classe="COMERCIAL",
        consumo_ponta_kwh=1000.0,
        consumo_fora_ponta_kwh=9000.0,
        demanda_ponta_kw=50.0,
        demanda_fora_ponta_kw=100.0,
    )
    base.update(overrides)
    return Consumidor(**base)


def test_consumidor_aceita_perfil_valido():
    cons = _consumidor_valido()
    assert cons.consumo_total_kwh == 10000.0


def test_consumidor_campos_obrigatorios_textuais_nao_vazios():
    for campo in ("distribuidora", "subgrupo", "classe"):
        with pytest.raises(ValueError):
            _consumidor_valido(**{campo: " "})


def test_consumidor_rejeita_valores_negativos():
    for campo in (
        "consumo_ponta_kwh",
        "consumo_fora_ponta_kwh",
        "demanda_ponta_kw",
        "demanda_fora_ponta_kw",
    ):
        with pytest.raises(ValueError):
            _consumidor_valido(**{campo: -1.0})


def test_consumidor_aceita_zero_para_postos_ausentes():
    cons = _consumidor_valido(consumo_ponta_kwh=0.0, demanda_ponta_kw=0.0)
    assert cons.consumo_ponta_kwh == 0.0
    assert cons.demanda_ponta_kw == 0.0


def test_resultado_calculo_totais_por_componente_e_grandeza():
    parcelas = (
        ParcelaCusto("TE", GRANDEZA_ENERGIA, "PONTA", 1.0, 300.0, 300.0),
        ParcelaCusto("TUSD", GRANDEZA_ENERGIA, "PONTA", 1.0, 100.0, 100.0),
        ParcelaCusto("TUSD", GRANDEZA_DEMANDA, "PONTA", 2.0, 50.0, 100.0),
    )
    resultado = ResultadoCalculo(modalidade="AZUL", parcelas=parcelas)
    assert resultado.custo_te == 300.0
    assert resultado.custo_tusd == 200.0
    assert resultado.custo_energia == 400.0
    assert resultado.custo_demanda == 100.0
    assert resultado.custo_total == 500.0


def test_resultado_calculo_rejeita_modalidade_vazia():
    with pytest.raises(ValueError):
        ResultadoCalculo(modalidade=" ")
