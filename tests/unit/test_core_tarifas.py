"""Testes unitários de representação e seleção de tarifas (core/tarifas.py)."""

from datetime import date

import pytest

from core.tarifas import (
    AmbiguidadeTarifaria,
    ParcelaTarifaria,
    TarifaAcr,
    TarifaNaoEncontrada,
    buscar_tarifa,
    filtrar_tarifas,
    selecionar_unica,
    tarifas_vigentes,
)

D1 = date(2024, 1, 1)
D2 = date(2024, 7, 1)


def _tarifa(**overrides):
    base = dict(distribuidora="DIST", resolucao="REH0001", modalidade="AZUL")
    base.update(overrides)
    return TarifaAcr(**base)


def _parcela(**overrides):
    base = dict(
        componente="TE",
        grandeza="ENERGIA",
        posto="PONTA",
        unidade="R$/MWh",
        valor=300.0,
    )
    base.update(overrides)
    return ParcelaTarifaria(**base)


# --- TarifaAcr ------------------------------------------------------------

def test_tarifa_acr_rejeita_campos_obrigatorios_vazios():
    with pytest.raises(ValueError):
        _tarifa(distribuidora=" ")
    with pytest.raises(ValueError):
        _tarifa(resolucao="")


def test_tarifa_acr_rejeita_valores_negativos():
    with pytest.raises(ValueError):
        _tarifa(tusd=-1.0)
    with pytest.raises(ValueError):
        _tarifa(te=-1.0)


def test_tarifa_acr_rejeita_vigencia_invertida():
    with pytest.raises(ValueError):
        _tarifa(inicio_vigencia=D2, fim_vigencia=D1)


# --- ParcelaTarifaria (normalização do contrato) ---------------------------

def test_parcela_normaliza_valores_de_texto_para_maiusculas():
    parcela = _parcela(
        componente=" te ", grandeza="energia", posto="ponta", unidade="R$/MWh"
    )
    assert parcela.componente == "TE"
    assert parcela.grandeza == "ENERGIA"
    assert parcela.posto == "PONTA"


def test_parcela_rejeita_componente_grandeza_ou_posto_nao_suportado():
    with pytest.raises(ValueError):
        _parcela(componente="TRIBUTOS")
    with pytest.raises(ValueError):
        _parcela(grandeza="REATIVOS")
    with pytest.raises(ValueError):
        _parcela(posto="INTERMEDIARIO")


def test_parcela_rejeita_unidade_vazia_ou_valor_negativo():
    with pytest.raises(ValueError):
        _parcela(unidade=" ")
    with pytest.raises(ValueError):
        _parcela(valor=-0.01)


# --- Filtros ---------------------------------------------------------------

def test_filtrar_tarifas_e_case_insensitive():
    tarifas = [
        _tarifa(modalidade="AZUL"),
        _tarifa(resolucao="REH0002", modalidade="VERDE"),
    ]
    selecionadas = filtrar_tarifas(tarifas, modalidade="azul")
    assert [t.modalidade for t in selecionadas] == ["AZUL"]


def test_filtrar_tarifas_ignora_filtros_nulos():
    tarifas = [_tarifa(), _tarifa(resolucao="REH0002")]
    assert filtrar_tarifas(tarifas) == tarifas


# --- Vigência --------------------------------------------------------------

def test_tarifas_vigentes_intervalo_inclusivo():
    em_vigencia = _tarifa(inicio_vigencia=D1, fim_vigencia=D2)
    tarifas = [
        em_vigencia,
        _tarifa(inicio_vigencia=date(2025, 1, 1)),
        _tarifa(fim_vigencia=date(2023, 12, 31)),
    ]
    assert tarifas_vigentes(tarifas, D1) == [em_vigencia]
    assert tarifas_vigentes(tarifas, D2) == [em_vigencia]
    assert tarifas_vigentes(tarifas, date(2024, 3, 1)) == [em_vigencia]


def test_tarifas_vigentes_aceita_limites_abertos():
    sem_inicio = _tarifa(inicio_vigencia=None, fim_vigencia=D2)
    sem_fim = _tarifa(inicio_vigencia=D1, fim_vigencia=None)
    assert tarifas_vigentes([sem_inicio], date(2000, 1, 1)) == [sem_inicio]
    assert tarifas_vigentes([sem_fim], date(2099, 1, 1)) == [sem_fim]


# --- Seleção única -----------------------------------------------------------

def test_selecionar_unica_retorna_tarifa_quando_unica():
    t = _tarifa()
    assert selecionar_unica([t]) is t


def test_selecionar_unica_lanca_quando_vazio_ou_multiplo():
    t = _tarifa()
    with pytest.raises(TarifaNaoEncontrada):
        selecionar_unica([])
    with pytest.raises(AmbiguidadeTarifaria):
        selecionar_unica([t, _tarifa(resolucao="REH0002")])


# --- Busca integrada ------------------------------------------------------

def test_buscar_tarifa_aplica_vigencia_e_filtros():
    alvo = _tarifa(
        inicio_vigencia=D1,
        fim_vigencia=D2,
        subgrupo="A4",
        classe="COMERCIAL",
        posto="P",
    )
    ruido = _tarifa(
        resolucao="REH0099",
        inicio_vigencia=date(2025, 1, 1),
        subgrupo="A4",
        classe="COMERCIAL",
        posto="P",
    )
    encontrada = buscar_tarifa(
        [alvo, ruido],
        date(2024, 3, 1),
        distribuidora="DIST",
        subgrupo="A4",
        classe="COMERCIAL",
        posto="P",
    )
    assert encontrada is alvo


def test_buscar_tarifa_lanca_quando_nenhuma_corresponde():
    with pytest.raises(TarifaNaoEncontrada):
        buscar_tarifa([], D1, distribuidora="DIST")
