"""Testes obrigatórios do planejamento anual (core/planejamento.py)."""

import pytest

from core.planejamento import (
    AVISO_DEMANDA_PONTA_ESTIMADA,
    DC_MINIMO_GRUPO_A,
    MedicaoMensal,
    _contrato_para_dc,
    comparar_planejamento,
    custo_demanda_mensal,
    decompor_ganho,
    demanda_ponta_equilibrio,
    montar_demanda,
    montar_demandas,
    otimizar_contrato,
    otimizar_contrato_azul,
    ResultadoModalidadePlanejamento,
)

D_PONTA = [193, 210, 203, 217, 189, 154, 168, 179, 189, 203, 151, 95]
D_FORA = [200, 231, 214, 238, 179, 140, 151, 168, 189, 207, 165, 98]
D_VERDE = [max(p, f) for p, f in zip(D_PONTA, D_FORA)]
T_DEM = 30.0


def _fn_sintetica(medidas, tarifa=T_DEM):
    return lambda dc, i: custo_demanda_mensal(medidas[i], dc, tarifa)


def test_verde_otimiza_dc_204_e_referencias():
    fn = _fn_sintetica(D_VERDE)
    r = otimizar_contrato(D_VERDE, fn)

    assert r.dc == 204.0
    assert r.custo_anual == pytest.approx(79_320.0)
    assert _contrato_para_dc(200.0, D_VERDE, fn).custo_anual == pytest.approx(79_680.0)
    assert _contrato_para_dc(238.0, D_VERDE, fn).custo_anual == pytest.approx(85_680.0)


def test_azul_otimiza_ponta_194_e_fora_204():
    fn_ponta = _fn_sintetica(D_PONTA)
    fn_fora = _fn_sintetica(D_FORA)

    def custo_posto(posto, dc, i):
        return fn_ponta(dc, i) if posto == "PONTA" else fn_fora(dc, i)

    r = otimizar_contrato_azul(D_PONTA, D_FORA, custo_posto)

    assert r.ponta.dc == 194.0
    assert r.ponta.custo_anual == pytest.approx(73_890.0)
    assert r.fora_ponta.dc == 204.0
    assert r.fora_ponta.custo_anual == pytest.approx(79_320.0)


def test_demanda_ausente_usa_unica_com_aviso():
    demanda, aviso = montar_demanda(MedicaoMensal(d_med_unica=200.0))

    assert demanda.azul_ponta == 200.0
    assert demanda.azul_fora_ponta == 200.0
    assert demanda.verde == 200.0
    assert aviso == AVISO_DEMANDA_PONTA_ESTIMADA


def test_demanda_com_split_prevalece():
    demanda, aviso = montar_demanda(
        MedicaoMensal(d_med_ponta=193.0, d_med_fora_ponta=200.0)
    )

    assert demanda.azul_ponta == 193.0
    assert demanda.azul_fora_ponta == 200.0
    assert demanda.verde == 200.0
    assert aviso is None


def test_meses_parciais_gera_aviso():
    _, avisos = montar_demandas([MedicaoMensal(d_med_unica=100.0)] * 6)
    assert any("parciais" in a for a in avisos)


def test_equilibrio_por_bissecao():
    def custo_azul(dp):
        return 50_000.0 + 100.0 * dp

    r = demanda_ponta_equilibrio(custo_azul, custo_verde=51_000.0, d_med_unica=200.0)

    assert r.dp_eq == pytest.approx(10.0, abs=0.15)
    assert abs(custo_azul(r.dp_eq) - 51_000.0) < 20.0


def test_equilibrio_verde_sempre_melhor():
    r = demanda_ponta_equilibrio(
        lambda dp: 60_000.0 + dp, custo_verde=51_000.0, d_med_unica=200.0
    )
    assert r.dp_eq is None
    assert r.verde_sempre_melhor


def test_equilibrio_azul_sempre_melhor():
    r = demanda_ponta_equilibrio(
        lambda dp: 40_000.0 + dp, custo_verde=51_000.0, d_med_unica=200.0
    )
    assert r.dp_eq == pytest.approx(200.0)
    assert r.azul_sempre_melhor


def test_minimo_regulatorio_30kw():
    medidas = [10.0] * 12
    r = otimizar_contrato(medidas, _fn_sintetica(medidas))

    assert r.dc == DC_MINIMO_GRUPO_A


def test_empate_escolhe_menor_dc():
    from core.planejamento import CustoDemandaMensal

    def constante(dc, i):
        return CustoDemandaMensal(
            faturavel_kw=100.0, ultrapassagem_kw=0.0, ociosidade_kw=0.0, custo=100.0
        )

    r = otimizar_contrato([100.0] * 12, constante)

    assert r.dc == DC_MINIMO_GRUPO_A


def test_consistencia_contrato_atual_igual_referencia():
    fn = _fn_sintetica(D_VERDE)
    dc_atual = 200.0
    referencia = _contrato_para_dc(dc_atual, D_VERDE, fn)
    esperado = sum(custo_demanda_mensal(d, dc_atual, T_DEM).custo for d in D_VERDE)

    assert referencia.custo_anual == pytest.approx(esperado)
    assert referencia.custo_anual == pytest.approx(79_680.0)


def test_consistencia_demanda_sintetica_igual_motor():
    """A parcela de demanda do custo sintético é igual à linha do motor."""
    from core.motor_calculo import calcular_fatura
    from core.models import Consumidor
    from core.tarifas import ParcelaTarifaria

    tarifa = 30.0
    dc, d_med = 204.0, 238.0
    parcela = ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", tarifa)
    consumidor = Consumidor(
        distribuidora="SINTETICA",
        subgrupo="A4",
        classe="Não se aplica",
        demanda_medida_unica_kw=d_med,
        demanda_contratada_unica_kw=dc,
    )
    fatura = calcular_fatura(
        consumidor, "Verde", [parcela], demanda_unica=True,
        aplicar_tributos=False,
    )

    sintetico = custo_demanda_mensal(d_med, dc, tarifa).custo

    # A fatura tem 1 linha de demanda + 1 linha de ultrapassagem (sem
    # tributos); o total é exatamente a parcela sintética.
    assert fatura.custo_total == pytest.approx(sintetico)


def test_decomposicao_ganho():
    g = decompor_ganho(
        custo_atual_contrato_atual=1000.0,
        custo_atual_demanda_otima=900.0,
        custo_melhor_demanda_otima=800.0,
    )

    assert g.ganho_total == pytest.approx(200.0)
    assert g.ganho_demanda == pytest.approx(100.0)
    assert g.ganho_modalidade == pytest.approx(100.0)


def test_comparar_planejamento_decompoe_e_escolhe_melhor():
    resultados = [
        ResultadoModalidadePlanejamento(
            modalidade="Azul",
            custo_contrato_atual=1000.0,
            custo_demanda_otimizada=800.0,
            dc_atual=(200.0, 200.0),
            dc_otima=(194.0, 204.0),
            detalhe=None,  # type: ignore[arg-type]
        ),
        ResultadoModalidadePlanejamento(
            modalidade="Verde",
            custo_contrato_atual=900.0,
            custo_demanda_otimizada=850.0,
            dc_atual=200.0,
            dc_otima=204.0,
            detalhe=None,  # type: ignore[arg-type]
        ),
    ]

    r = comparar_planejamento(resultados, modalidade_atual="Verde")

    assert r.melhor_contrato_atual == "Verde"
    assert r.melhor_demanda_otimizada == "Azul"
    assert r.ganho.ganho_total == pytest.approx(900.0 - 800.0)
    assert r.ganho.ganho_demanda == pytest.approx(900.0 - 850.0)
    assert r.ganho.ganho_modalidade == pytest.approx(850.0 - 800.0)


def test_breakpoints_iguais_busca_exaustiva_sintetico():
    """Os pontos de quebra dão o MESMO resultado da busca exaustiva de 1 kW."""
    for medidas, fn in [
        (D_VERDE, _fn_sintetica(D_VERDE)),
        (D_PONTA, _fn_sintetica(D_PONTA)),
        (D_FORA, _fn_sintetica(D_FORA)),
    ]:
        rapido = otimizar_contrato(medidas, fn)  # breakpoints
        exaustivo = otimizar_contrato(medidas, fn, passo=1.0)
        assert rapido.dc == exaustivo.dc
        assert rapido.custo_anual == pytest.approx(exaustivo.custo_anual)
