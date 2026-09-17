"""Testes unitários dos schemas (P1). Não depende de banco nem de regra de
mercado — apenas validação de formato.
"""

import pytest
from pydantic import ValidationError

from schemas.calculo import ParcelaCustoOut, ResultadoCalculoOut
from schemas.consulta import (
    DistribuidoraOut,
    FiltroConsultaTarifa,
    TarifaConsultaOut,
)
from schemas.consumidor import MODALIDADES_MVP, Consumidor


# --------------------------------------------------------------------------- #
# Consumidor
# --------------------------------------------------------------------------- #
def _perfil(**over):
    base = dict(
        distribuidora="CPFL JAGUARI",
        subgrupo="A2",
        modalidade="Azul",
        consumo_ponta_kwh=1000.0,
        consumo_fora_ponta_kwh=9000.0,
        demanda_ponta_kw=100.0,
    )
    base.update(over)
    return Consumidor(**base)


def test_perfil_valido():
    p = _perfil()
    assert p.distribuidora == "CPFL JAGUARI"
    assert p.subgrupo == "A2"
    assert p.modalidade == "AZUL"  # normalize para caixa alta
    assert p.consumo_total_kwh == 10000.0


def test_perfil_sem_modalidade_aceita_none():
    p = _perfil(modalidade=None)
    assert p.modalidade is None


def test_perfil_aplica_modalidade_desconhecida():
    with pytest.raises(ValidationError):
        _perfil(modalidade="Roxa")


def test_perfil_obriga_distribuidora_e_subgrupo():
    with pytest.raises(ValidationError):
        _perfil(distribuidora="")
    with pytest.raises(ValidationError):
        _perfil(subgrupo="")


def test_perfil_rejeita_negativos():
    with pytest.raises(ValidationError):
        _perfil(consumo_ponta_kwh=-1)
    with pytest.raises(ValidationError):
        _perfil(demanda_fora_ponta_kw=-5)


def test_perfil_data_invalida():
    with pytest.raises(ValidationError):
        _perfil(data_referencia="2024/01/01")
    _perfil(data_referencia="2024-01-01")


def test_modalidades_mvp_presentes():
    assert {"AZUL", "VERDE"} <= set(MODALIDADES_MVP)


# --------------------------------------------------------------------------- #
# Consulta (leitura)
# --------------------------------------------------------------------------- #
def test_filtro_consulta_tudo_opcional():
    f = FiltroConsultaTarifa()
    assert f.num_cnpj is None and f.data is None and f.componente is None


def test_filtro_consulta_rejeita_componente_invalido():
    with pytest.raises(ValidationError):
        FiltroConsultaTarifa(componente="OUTRO")


def test_tarifa_consulta_out():
    t = TarifaConsultaOut(
        num_cnpj="123",
        sig_agente="DIST",
        componente="TUSD",
        valor=1.85,
        inicio_vigencia="2024-01-01",
        fim_vigencia="2024-12-31",
        base_tarifaria="Tarifa de Aplicação",
        subgrupo="A2",
        modalidade="Azul",
        classe="Não se aplica",
        subclasse="Não se aplica",
        detalhe="Não se aplica",
        posto="Fora ponta",
        unidade="MWh",
    )
    assert t.componente == "TUSD"
    assert t.valor == 1.85


def test_distribuidora_out_cnpj_identidade():
    d = DistribuidoraOut(num_cnpj="02016439000138", sig_agente="RGE")
    assert d.num_cnpj == "02016439000138"


# --------------------------------------------------------------------------- #
# Cálculo (forma; sem regra)
# --------------------------------------------------------------------------- #
def test_resultado_calculo_out_padrao():
    r = ResultadoCalculoOut(modalidade="AZUL")
    assert r.parcelas == []
    assert r.custo_total is None  # ainda sem regra


def test_parcela_custo_out():
    p = ParcelaCustoOut(componente="TE", grandeza="ENERGIA", posto="PONTA")
    assert p.componente == "TE"
