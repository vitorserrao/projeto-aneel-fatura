"""PlanejamentoService sem banco: a demanda medida do histórico chega ao motor.

Regressão: com histórico por posto (d_med_ponta/d_med_fora_ponta), a Verde
lia só ``d_med_unica`` e faturava demanda medida 0 — a DC ótima caía no
mínimo de 30 kW e o "ganho" do ajuste de demanda saía inflado.
"""
from datetime import date

from core.models import Consumidor
from core.tarifas import ParcelaTarifaria
from services.planejamento_service import PlanejamentoService

# Tarifas fictícias (R$/kW e R$/MWh) só para exercitar o serviço.
_PARCELAS = {
    "Verde": [
        ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 20.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 1000.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 100.0),
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 450.0),
        ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 280.0),
    ],
    "Azul": [
        ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 60.0),
        ParcelaTarifaria("TUSD", "DEMANDA", "FORA PONTA", "R$/kW", 20.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 100.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 100.0),
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 450.0),
        ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 280.0),
    ],
}


class _RepoFake:
    def buscar_bandeira(self, _data):
        return None


class _CalculoFake:
    _repo = _RepoFake()

    def parcelas_vigentes(self, _consumidor, modalidade, _base):
        return list(_PARCELAS[modalidade.strip().title()]), [], [], modalidade == "Verde"


class _EpiFake:
    def _buscar_te(self, _perfil, _modalidade, _data):
        return 450.0, 280.0


def _historico(dp, dfp):
    return [
        {"data_referencia": f"2023-{m:02d}-15", "d_med_ponta": p, "d_med_fora_ponta": f,
         "e_ponta_kwh": 5000.0, "e_fora_ponta_kwh": 50000.0}
        for m, (p, f) in enumerate(zip(dp, dfp), start=1)
    ]


def _comparar(meses, **kw):
    servico = PlanejamentoService(_CalculoFake(), _EpiFake())
    perfil = Consumidor(distribuidora="X", subgrupo="A4", classe="Não se aplica",
                        detalhe="Não se aplica", data_referencia=date(2023, 12, 15))
    return servico.comparar(perfil, meses, pis=0.01, cofins=0.04, icms=0.18,
                            dc_atual_verde=400.0, dc_atual_azul_ponta=400.0,
                            dc_atual_azul_fora=400.0, **kw)


def test_verde_usa_max_ponta_fora_do_historico():
    dp = [150.0] * 12
    dfp = [180.0] * 11 + [200.0]
    plano, _ = _comparar(_historico(dp, dfp))
    verde = next(m for m in plano.modalidades if m.modalidade == "Verde")
    # A DC ótima tem de ficar perto da demanda medida, nunca no mínimo de 30 kW.
    assert verde.dc_otima >= 180.0
    # Com DC ótima a fatura cobra no mínimo a demanda medida de cada mês.
    assert verde.custo_demanda_otimizada > 12 * 180.0 * 20.0


def test_so_demanda_unica_vale_para_os_dois_postos_da_azul():
    meses = [
        {"data_referencia": f"2023-{m:02d}-15", "d_med_unica": 200.0,
         "e_ponta_kwh": 5000.0, "e_fora_ponta_kwh": 50000.0}
        for m in range(1, 13)
    ]
    plano, _ = _comparar(meses)
    azul = next(m for m in plano.modalidades if m.modalidade == "Azul")
    dc_ponta, dc_fora = azul.dc_otima
    assert dc_ponta >= 190.0 and dc_fora >= 190.0


def test_contrato_atual_reproduz_fatura_real_copel():
    """O cenário 'contrato atual' do planejamento bate com a fatura Copel 04/2023.

    Tarifas líquidas impressas na fatura; soma técnica sem CIP e sem reativo:
    27,49 + 72,79 + 2.895,85 + 1.298,56 + 3.411,60 + 2.030,63 = 9.736,92.
    Antes da correção, a demanda medida entrava como 0 e a demanda isenta de
    ICMS não era aplicada (+R$ 445,75).
    """
    verde = [
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 388.08),
        ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 247.20),
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 1027.46),
        ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 110.85),
        ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 17.58),
    ]
    tabela = {"Verde": verde, "Azul": verde + [ParcelaTarifaria("TUSD", "DEMANDA", "FORA PONTA", "R$/kW", 17.58)]}

    class _Calc(_CalculoFake):
        def parcelas_vigentes(self, _c, modalidade, _b):
            return list(tabela[modalidade.strip().title()]), [], [], modalidade == "Verde"

    servico = PlanejamentoService(_Calc(), _EpiFake())
    perfil = Consumidor(distribuidora="COPEL-DIS", subgrupo="A4", classe="Não se aplica",
                        detalhe="Não se aplica", data_referencia=date(2023, 3, 15))
    mes = [{"data_referencia": "2023-03-15", "d_med_ponta": 6.88, "d_med_fora_ponta": 150.65,
            "e_ponta_kwh": 55, "e_fora_ponta_kwh": 9094}]
    plano, _ = servico.comparar(perfil, mes, pis=0.0095, cofins=0.0438, icms=0.18,
                                dc_atual_verde=260.0, dc_atual_azul_ponta=260.0,
                                dc_atual_azul_fora=260.0)
    v = next(m for m in plano.modalidades if m.modalidade == "Verde")
    assert abs(v.custo_contrato_atual - 9736.92) <= 1.00


def test_mes_sem_consumo_levanta_value_error():
    """Dado faltante nunca vira zero: mês sem consumo ponta/fora é erro."""
    import pytest

    servico = PlanejamentoService(_CalculoFake(), _EpiFake())
    perfil = Consumidor(distribuidora="X", subgrupo="A4", classe="Não se aplica",
                        detalhe="Não se aplica", data_referencia=date(2023, 12, 15))
    mes = [{"data_referencia": "2023-01-15", "d_med_unica": 100.0}]  # sem consumo
    with pytest.raises(ValueError):
        servico.comparar(perfil, mes, pis=0.01, cofins=0.04, icms=0.18)
