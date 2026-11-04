"""Testes unitários do motor de fatura (estrutura do Simulador).

Cobrem: demanda faturável = máx(contratada, medida); ultrapassagem quando
medida excede contratada além de 5%; bandeira/encargo; reativos (fp < 0,92);
tributos opcionais; e ausência de duplicidade (P6 resolvido a montante pelo
filtro de detalhe).
"""

from datetime import date

import pytest

from core.motor_calculo import calcular_fatura
from core.models import Consumidor
from core.tarifas import ParcelaTarifaria


def _consumidor(**over):
    base = dict(
        distribuidora="DIST",
        subgrupo="A4",
        classe="Não se aplica",
        data_referencia=date(2024, 1, 1),
        detalhe="Não se aplica",
        consumo_ponta_kwh=100_000.0,
        consumo_fora_ponta_kwh=900_000.0,
        demanda_ponta_kw=1_000.0,
        demanda_fora_ponta_kw=2_000.0,
        demanda_contratada_ponta_kw=1_200.0,
        demanda_contratada_fora_ponta_kw=1_500.0,
    )
    base.update(over)
    return Consumidor(**base)


def _parcelas_azul():
    return [
        # demanda ponta (R$/kW) e fora ponta (R$/kW)
        ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 20.0),
        ParcelaTarifaria("TUSD", "DEMANDA", "FORA PONTA", "R$/kW", 10.0),
        # energia TUSD (R$/MWh)
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 300.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 200.0),
        # TE (R$/MWh)
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 400.0),
        ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 350.0),
    ]


def test_fatura_azul_demanda_faturavel_e_sem_duplicidade():
    fatura = calcular_fatura(_consumidor(), "Azul", _parcelas_azul())
    linhas_demanda_ponta = [
        l for l in fatura.linhas if l.descricao == "TUSD DEMANDA PONTA"
    ]
    assert len(linhas_demanda_ponta) == 1
    assert linhas_demanda_ponta[0].quantidade == 1_200.0  # contratada > medida

    # demanda fora ponta usa a MEDIDA (2000 > 1500 contratada)
    linhas_demanda_fp = [
        l for l in fatura.linhas if l.descricao == "TUSD DEMANDA FORA PONTA"
    ]
    assert linhas_demanda_fp[0].quantidade == 2_000.0


def test_ultrapassagem_quando_excede_5_porcento():
    fatura = calcular_fatura(_consumidor(), "Azul", _parcelas_azul())
    ult = [l for l in fatura.linhas if l.categoria == "ULTRAPASSAGEM"]
    # fora ponta: medida 2000, contratada 1500 -> gatilho (2000 > 1575) e
    # base excedente total = 2000 - 1500 = 500 (interpretação B do slide).
    assert ult, "deveria haver ultrapassagem"
    fora = [l for l in ult if "FORA PONTA" in l.descricao]
    assert fora
    assert abs(fora[0].quantidade - 500.0) < 1e-6
    # tarifa de ultrapassagem = 2x tarifa de demanda (10.0) -> 20.0
    assert abs(fora[0].tarifa - 20.0) < 1e-6


def test_bandeira_e_cip():
    fatura = calcular_fatura(
        _consumidor(bandeira_adicional_r_kwh=0.02, cip_cosip_rs=50.0),
        "Azul",
        _parcelas_azul(),
    )
    categorias = {l.categoria for l in fatura.linhas}
    assert "BANDEIRA" in categorias
    assert "ENCARGO" in categorias
    total = fatura.custo_total
    assert total > 0


def test_reativos_excedentes_com_tarifas_de_referencia():
    # Sem tarifa de referência o motor NÃO inventa linha de reativos; com
    # vrere/vrdre e fp < 0,92 a linha é emitida (regra art. 304).
    consumidor = _consumidor(
        reativo_energia_ponta_kvArh=600_000.0,
        reativo_energia_fora_ponta_kvArh=0.0,
    )
    sem = calcular_fatura(consumidor, "Azul", _parcelas_azul())
    assert not [l for l in sem.linhas if l.categoria == "REATIVOS"]

    com = calcular_fatura(
        consumidor,
        "Azul",
        _parcelas_azul(),
        vrere_r_mwh=350.0,
        vrdre_r_kw=10.0,
    )
    reat = [l for l in com.linhas if l.categoria == "REATIVOS"]
    assert reat, "fator de potência baixo deveria gerar linha de reativos"


def test_tributos_opcionais():
    sem = calcular_fatura(_consumidor(), "Azul", _parcelas_azul(), aplicar_tributos=False)
    com = calcular_fatura(
        _consumidor(),
        "Azul",
        _parcelas_azul(),
        aplicar_tributos=True,
        pis=0.0025,
        cofins=0.0115,
        icms=0.25,
    )
    assert com.custo_total > sem.custo_total


def test_sem_tarifa_lanca_erro():
    with pytest.raises(ValueError):
        calcular_fatura(_consumidor(), "Azul", [])
