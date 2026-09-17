"""Testes do adapter Repository → Core (P2). Não depende de banco."""

from datetime import date
from decimal import Decimal

import pytest

from core.tarifas import TarifaAcr
from infra.repositories.adapter import (
    tarifa_vigente_para_parcela,
    tarifa_vigente_para_tarifa_acr,
)
from infra.repositories.tarifa_repository import TarifaVigente


def _tusd_vigente(**over):
    base = dict(
        num_cnpj="02016439000138",
        sig_agente="RGE",
        componente="TUSD",
        valor=Decimal("1.85"),
        resolucao="REH TESTE 1234",
        inicio_vigencia=date(2024, 1, 1),
        fim_vigencia=date(2024, 12, 31),
        base_tarifaria="Tarifa de Aplicação",
        subgrupo="A2",
        modalidade="Azul",
        classe="Não se aplica",
        subclasse="Não se aplica",
        detalhe="Não se aplica",
        posto="Fora ponta",
        unidade="kW",
    )
    base.update(over)
    return TarifaVigente(**base)


def test_tarifa_vigente_para_tarifa_acr_perda_zero():
    v = _tusd_vigente()
    acr = tarifa_vigente_para_tarifa_acr(v)
    assert isinstance(acr, TarifaAcr)
    assert acr.distribuidora == "RGE"
    assert acr.subgrupo == "A2"
    assert acr.modalidade == "Azul"
    assert acr.posto == "Fora ponta"
    assert acr.unidade == "kW"
    assert acr.tusd == 1.85
    assert acr.te == 0.0  # componente é TUSD
    assert acr.inicio_vigencia == date(2024, 1, 1)


def test_tarifa_vigente_para_parcela_exige_grandeza_e_posto():
    v = _tusd_vigente()
    p = tarifa_vigente_para_parcela(
        v, grandeza="DEMANDA", posto="FORA PONTA"
    )
    assert p.componente == "TUSD"
    assert p.grandeza == "DEMANDA"
    assert p.posto == "FORA PONTA"
    assert p.unidade == "R$/kW"
    assert p.valor == 1.85


def test_tarifa_vigente_para_parcela_traduz_unidade_mwh():
    v = _tusd_vigente(componente="TE", unidade="MWh", valor=Decimal("300.000000"))
    p = tarifa_vigente_para_parcela(v, grandeza="ENERGIA", posto="PONTA")
    assert p.componente == "TE"
    assert p.unidade == "R$/MWh"
    assert p.grandeza == "ENERGIA"
    assert p.posto == "PONTA"


def test_parcela_unidade_desconhecida_falha():
    v = _tusd_vigente(unidade="kvarh")
    with pytest.raises(ValueError):
        tarifa_vigente_para_parcela(v, grandeza="DEMANDA", posto="PONTA")


def test_componente_te_na_acr_coloca_apenas_te():
    v = _tusd_vigente(componente="TE", unidade="MWh")
    acr = tarifa_vigente_para_tarifa_acr(v)
    assert acr.te == 1.85
    assert acr.tusd == 0.0
