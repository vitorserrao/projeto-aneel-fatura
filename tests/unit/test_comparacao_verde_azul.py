"""Testes da comparação Verde × Azul (níveis 1 e 2) com tarifas fictícias.

As tarifas abaixo existem APENAS neste teste (nunca no código de produção);
na aplicação real elas vêm do TarifaRepository.
"""

from datetime import date

import pytest

from core.models import Consumidor
from core.tarifas import ParcelaTarifaria
from services.comparacao_verde_azul import ComparacaoVerdeAzulService


class _RepoFake:
    def buscar_bandeira(self, competencia):
        return None


class _CalculoFake:
    _repo = _RepoFake()

    def parcelas_vigentes(self, consumidor, modalidade, base_tarifaria):
        if modalidade.strip().title() == "Verde":
            parcelas = [
                ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 20.0),
                ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 200.0),
                ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 100.0),
                ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 300.0),
                ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 200.0),
            ]
        else:
            parcelas = [
                ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 30.0),
                ParcelaTarifaria("TUSD", "DEMANDA", "FORA PONTA", "R$/kW", 15.0),
                ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 200.0),
                ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 100.0),
                ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 300.0),
                ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 200.0),
            ]
        return parcelas, [], [], modalidade.strip().title() == "Verde"

    def _buscar_vrere(self, consumidor, base):
        return None, None

    def _buscar_vrdre(self, consumidor, base):
        return None, None


def _perfil():
    return Consumidor(
        distribuidora="DIST",
        subgrupo="A4",
        classe="Não se aplica",
        data_referencia=None,
        detalhe="Não se aplica",
    )


def _mes(contratada_ref=None, **over):
    mes = {
        "data_referencia": "2024-12-15",
        "data_leitura_anterior": "2024-12-01",
        "data_leitura_atual": "2024-12-31",
        "dp": None,
        "dfp": None,
        "d_verde": 60.0,
        "ep_kwh": 1260.0,
        "efp_kwh": 4000.0,
    }
    mes.update(over)
    return mes


@pytest.fixture
def servico():
    return ComparacaoVerdeAzulService(_CalculoFake())


def test_nivel2_veredito_verde(servico):
    # Contratada atual igual à ótima da Verde (60/1,05): fatura Verde mínima.
    resultado = servico.comparar(
        _perfil(),
        [_mes()],
        pis=0.0,
        cofins=0.0,
        icms=0.0,
        contratada_atual=60.0 / 1.05,
    )
    assert resultado.nivel == 2
    assert resultado.veredito == "VERDE"
    assert resultado.azul["min"] > resultado.verde_atual


def test_nivel2_veredito_azul(servico):
    # Contratada atual alta: a Verde fica acima até da Azul máxima.
    resultado = servico.comparar(
        _perfil(),
        [_mes()],
        pis=0.0,
        cofins=0.0,
        icms=0.0,
        contratada_atual=150.0,
    )
    assert resultado.nivel == 2
    assert resultado.veredito == "AZUL"
    assert resultado.verde_atual > resultado.azul["max"]


def test_nivel2_inconclusivo_com_dp_equilibrio_na_faixa(servico):
    resultado = servico.comparar(
        _perfil(),
        [_mes()],
        pis=0.0,
        cofins=0.0,
        icms=0.0,
        contratada_atual=30.0,
    )
    assert resultado.nivel == 2
    assert resultado.veredito == "INCONCLUSIVO"
    assert resultado.azul["min"] <= resultado.verde_atual <= resultado.azul["max"]
    assert resultado.dp_equilibrio is not None
    # Faixa do mês: mínimo = 1260/63 = 20; máximo = 60. O piso de 30 kW entra
    # na CONTRATADA (otimizar_contratada), não na faixa medida.
    assert 30.0 <= resultado.dp_equilibrio <= 60.0
    # Com as tarifas fictícias, o equilíbrio fica em ~50 kW.
    assert resultado.dp_equilibrio == pytest.approx(50.0, abs=0.5)
    # A estimativa central nunca é usada para decidir.
    assert resultado.dc_otimas["p"]["min"] != resultado.dc_otimas["p"]["max"]


def test_nivel2_nunca_usa_meio_da_faixa_para_decidir(servico):
    # Mesmo caso inconclusivo: o veredito não pode depender do ponto médio.
    resultado = servico.comparar(
        _perfil(),
        [_mes()],
        pis=0.0,
        cofins=0.0,
        icms=0.0,
        contratada_atual=30.0,
    )
    assert resultado.veredito == "INCONCLUSIVO"
    assert resultado.dp_equilibrio is not None


def test_dado_ausente_nao_vira_zero_e_exclui_mes(servico):
    resultado = servico.comparar(
        _perfil(),
        [
            _mes(),
            _mes(
                data_referencia="2024-11-15",
                ep_kwh=None,  # ausente — NÃO é 0
            ),
        ],
        pis=0.0,
        cofins=0.0,
        icms=0.0,
        contratada_atual=30.0,
    )
    assert resultado.meses_analisados == 1
    assert any("excluído" in a for a in resultado.avisos)


def test_nivel1_com_historico_ponta_e_fora(servico):
    resultado = servico.comparar(
        _perfil(),
        [
            {
                "data_referencia": "2024-12-15",
                "dp": 40.0,
                "dfp": 60.0,
                "ep_kwh": 1260.0,
                "efp_kwh": 4000.0,
            }
        ],
        pis=0.0,
        cofins=0.0,
        icms=0.0,
        contratada_atual=30.0,
    )
    assert resultado.nivel == 1
    assert isinstance(resultado.azul, float)
    # Nível 1 devolve resultado exato: delta = Verde atual − Azul.
    delta = resultado.verde_atual - resultado.azul
    if delta > 0:
        assert resultado.veredito == "AZUL"
    elif delta < 0:
        assert resultado.veredito == "VERDE"
    else:
        assert resultado.veredito == "INCONCLUSIVO"
    assert set(resultado.dc_otimas) == {"p", "fp", "verde"}


def test_um_mes_gera_aviso_de_sazonalidade(servico):
    resultado = servico.comparar(
        _perfil(),
        [_mes()],
        pis=0.0,
        cofins=0.0,
        icms=0.0,
        contratada_atual=30.0,
    )
    assert any("sazonalidade" in a for a in resultado.avisos)


def test_contratada_ausente_usa_piso_com_aviso(servico):
    resultado = servico.comparar(
        _perfil(),
        [_mes()],
        pis=0.0,
        cofins=0.0,
        icms=0.0,
        contratada_atual=None,
    )
    assert any("demanda mínima" in a for a in resultado.avisos)
