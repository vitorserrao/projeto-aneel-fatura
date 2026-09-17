"""Testes de elegibilidade de modalidades (core)."""

from datetime import date

from core.motor_calculo import (
    MODALIDADES_GRUPO_A,
    modalidades_elegiveis,
    motivo_indisponibilidade,
)
from core.models import Consumidor


def _consumidor(subgrupo="A4", demanda=100.0):
    return Consumidor(
        distribuidora="DIST",
        subgrupo=subgrupo,
        classe="Não se aplica",
        data_referencia=date(2024, 1, 1),
        detalhe="Não se aplica",
        demanda_ponta_kw=demanda,
        demanda_fora_ponta_kw=demanda,
    )


def test_azul_sempre_elegivel():
    assert "AZUL" in modalidades_elegiveis(_consumidor())


def test_verde_apenas_subgrupos_especificos():
    assert "VERDE" in modalidades_elegiveis(_consumidor("A4"))
    assert "VERDE" in modalidades_elegiveis(_consumidor("A3A"))
    assert "VERDE" in modalidades_elegiveis(_consumidor("AS"))
    assert "VERDE" not in modalidades_elegiveis(_consumidor("A2"))
    assert "VERDE" not in modalidades_elegiveis(_consumidor("A3"))


def test_motivos_indisponibilidade():
    assert motivo_indisponibilidade("AZUL", _consumidor("A2")) is None
    assert motivo_indisponibilidade("VERDE", _consumidor("A4")) is None
    assert "A3a, A4 e AS" in motivo_indisponibilidade("VERDE", _consumidor("A2"))
    assert motivo_indisponibilidade("BRANCA", _consumidor("A4")) is not None


def test_modalidades_grupo_a_catalogo():
    assert MODALIDADES_GRUPO_A == ("AZUL", "VERDE")
